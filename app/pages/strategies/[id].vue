<template>
  <div class="page-container">
    <div v-if="strategy">
      <h1>{{ strategy.name }}</h1>
      <p class="strategy-description">{{ strategy.description }}</p>

      <div class="details-grid">
        <div class="detail-item">
          <span class="label">Total Capital</span>
          <span class="value">{{ formatCurrency(strategy.capital) }}</span>
        </div>
        <div class="detail-item">
          <span class="label">Capital Used</span>
          <span class="value">{{ formatCurrency(strategy.capital_used) }}</span>
        </div>
        <div class="detail-item">
          <span class="label">Capital Available</span>
          <span class="value">{{ formatCurrency(strategy.capital_remaining) }}</span>
        </div>
        <div class="detail-item">
          <span class="label">Units</span>
          <span class="value">{{ strategy.units }}</span>
        </div>
      </div>

      <div class="performance-section">
        <h2>Performance</h2>
        <div class="details-grid">
          <div class="detail-item">
            <span class="label">Realized P&L</span>
            <span class="value" :class="pnlClass(strategy.pnl)">
              {{ formatCurrency(strategy.pnl) }}
            </span>
          </div>
          <div class="detail-item">
            <span class="label">Unrealized P&L</span>
            <span class="value" :class="pnlClass(strategy.unrealized_pnl)">
              {{ formatCurrency(strategy.unrealized_pnl) }}
            </span>
          </div>
          <div class="detail-item">
            <span class="label">Status</span>
            <span class="value">{{ strategy.is_active ? 'Active' : 'Inactive' }}</span>
          </div>
          <div class="detail-item">
            <span class="label">Created</span>
            <span class="value">{{ new Date(strategy.created_at).toLocaleDateString() }}</span>
          </div>
        </div>
      </div>

      <div class="actions">
        <button class="btn btn-primary" @click="openInvestDialog">
          Invest
        </button>
        <button class="btn btn-outline" @click="openWithdrawDialog">
          Withdraw
        </button>
      </div>
    </div>

    <div v-else>
      <p>Loading strategy details or strategy not found...</p>
    </div>

    <!-- Investment Dialog -->
    <dialog ref="investDialog" class="dialog">
      <div class="dialog-content">
        <h3>Invest in {{ strategy?.name }}</h3>
        <div class="form-group">
          <label for="investAmount">Amount to Invest</label>
          <input type="number" id="investAmount" v-model="investAmount" class="input" placeholder="Enter amount"
            min="0" />
        </div>
        <div class="dialog-actions">
          <button class="btn btn-outline" @click="closeInvestDialog">Cancel</button>
          <button class="btn btn-primary" @click="confirmInvestment">Confirm</button>
        </div>
      </div>
    </dialog>

    <!-- Withdraw Dialog -->
    <dialog ref="withdrawDialog" class="dialog">
      <div class="dialog-content">
        <h3>Withdraw from {{ strategy?.name }}</h3>
        <div class="form-group">
          <label for="withdrawAmount">Amount to Withdraw</label>
          <input type="number" id="withdrawAmount" v-model="withdrawAmount" class="input" placeholder="Enter amount"
            min="0" :max="strategy?.capital_used || 0" />
        </div>
        <div class="dialog-actions">
          <button class="btn btn-outline" @click="closeWithdrawDialog">Cancel</button>
          <button class="btn btn-primary" @click="confirmWithdrawal">Confirm</button>
        </div>
      </div>
    </dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useUserStore } from '~/store/user';

const route = useRoute();
const userStore = useUserStore();
const strategyId = computed(() => route.params.id as string)?.value;

interface Strategy {
  id: number;
  name: string;
  run_tf: string;
  description: string;
  capital: number;
  capital_remaining: number;
  capital_used: number;
  units: number;
  pnl: number;
  unrealized_pnl: number;
  is_active: boolean;
  created_at: string;
}

interface StrategyRes {
  is_error: boolean;
  is_success: boolean;
  message?: string;
  data?: Strategy;
}

const strategy = ref<Strategy | null | undefined>(null);
const investDialog = ref<HTMLDialogElement | null>(null);
const withdrawDialog = ref<HTMLDialogElement | null>(null);
const investAmount = ref<number>(0);
const withdrawAmount = ref<number>(0);

async function fetchStrategyById(id: number) {
  const runtimeConfig = useRuntimeConfig();
  const baseUrl = runtimeConfig.public.baseUrl;

  try {
    const url = `${baseUrl}/strategies/${id}`;
    const res: StrategyRes = await $fetch(url, {
      method: "GET",
    });

    if (res.is_error) {
      throw new Error(res.message || "Error fetching user data");
    }

    return res.data as Strategy;
  } catch (error) {
    console.error("Error fetching user:", error);
  }
}

onMounted(async () => {
  strategy.value = await fetchStrategyById(parseInt(strategyId));
});

const formatCurrency = (value: number) => {
  if (typeof value !== 'number') return 'N/A';
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'INR' }).format(value);
};

const pnlClass = (pnl: number) => {
  if (typeof pnl !== 'number') return 'pnl-neutral';
  if (pnl > 0) return 'pnl-positive';
  if (pnl < 0) return 'pnl-negative';
  return 'pnl-neutral';
};

// Dialog functions
const openInvestDialog = () => {
  investDialog.value?.showModal();
};

const closeInvestDialog = () => {
  investDialog.value?.close();
  investAmount.value = 0;
};

const openWithdrawDialog = () => {
  withdrawDialog.value?.showModal();
};

const closeWithdrawDialog = () => {
  withdrawDialog.value?.close();
  withdrawAmount.value = 0;
};

const investInStrategy = async (amount: number) => {
  const runtimeConfig = useRuntimeConfig();
  const baseUrl = runtimeConfig.public.baseUrl;

  try {
    const url = `${baseUrl}/strategies/invest`;
    const payload = {
      strategy_id: parseInt(strategyId),
      amount: amount
    };

    const res: StrategyRes = await $fetch(url, {
      method: "POST",
      body: payload,
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    });

    if (res.is_error) {
      throw new Error(res.message || "Error investing in strategy");
    }

    // Refresh strategy data after successful investment
    strategy.value = await fetchStrategyById(parseInt(strategyId));
  } catch (error) {
    console.error("Error investing in strategy:", error);
    throw error;
  }
};

const withdrawFromStrategy = async (amount: number) => {
  const runtimeConfig = useRuntimeConfig();
  const baseUrl = runtimeConfig.public.baseUrl;

  try {
    const url = `${baseUrl}/strategies/withdraw`;
    const payload = {
      strategy_id: parseInt(strategyId),
      amount: amount
    };

    const res: StrategyRes = await $fetch(url, {
      method: "POST",
      body: payload,
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    });

    if (res.is_error) {
      throw new Error(res.message || "Error withdrawing from strategy");
    }

    // Refresh strategy data after successful withdrawal
    strategy.value = await fetchStrategyById(parseInt(strategyId));
  } catch (error) {
    console.error("Error withdrawing from strategy:", error);
    throw error;
  }
};

const confirmInvestment = async () => {
  try {
    await investInStrategy(investAmount.value);
    closeInvestDialog();
  } catch (error) {
    console.error("Error during investment:", error);
    // Handle error (show notification, etc.)
  }
};

const confirmWithdrawal = async () => {
  try {
    await withdrawFromStrategy(withdrawAmount.value);
    closeWithdrawDialog();
  } catch (error) {
    console.error("Error during withdrawal:", error);
    // Handle error (show notification, etc.)
  }
};

definePageMeta({
  layout: 'default'
});
</script>

<style scoped>
.page-container {
  padding: 30px;
  background-color: #ffffff;
  border-radius: 8px;
  margin: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

h1 {
  font-size: 2.2em;
  color: #1A237E;
  margin-bottom: 10px;
}

.strategy-description {
  font-size: 1.1em;
  color: #555;
  margin-bottom: 25px;
  line-height: 1.6;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.detail-item {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 6px;
  border: 1px solid #e8e8e8;
}

.detail-item .label {
  display: block;
  font-size: 0.9em;
  color: #666;
  margin-bottom: 5px;
  font-weight: 500;
}

.detail-item .value {
  font-size: 1.1em;
  font-weight: bold;
  color: #333;
}

.performance-section,
.investment-details-section {
  margin-bottom: 30px;
}

.performance-section h2,
.investment-details-section h2 {
  font-size: 1.6em;
  color: #283593;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.pnl-positive {
  color: #2E7D32;
}

.pnl-negative {
  color: #C62828;
}

.pnl-neutral {
  color: #555;
}

.actions {
  margin-top: 30px;
  display: flex;
  gap: 15px;
  align-items: center;
}

.btn {
  padding: 10px 20px;
  border-radius: 5px;
  text-decoration: none;
  font-size: 1em;
  cursor: pointer;
  transition: background-color 0.2s ease, border-color 0.2s ease;
  border: 1px solid transparent;
}

.btn-primary {
  background-color: #FFC107;
  color: #333;
  font-weight: bold;
}

.btn-primary:hover {
  background-color: #FFB300;
}

.btn-outline {
  background-color: transparent;
  border-color: #3949AB;
  color: #3949AB;
}

.btn-outline:hover {
  background-color: #e8eaf6;
}

.dialog {
  border: none;
  border-radius: 8px;
  padding: 0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.dialog::backdrop {
  background: rgba(0, 0, 0, 0.5);
}

.dialog-content {
  padding: 24px;
  min-width: 300px;
}

.dialog h3 {
  margin: 0 0 20px 0;
  color: #1A237E;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #666;
}

.input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1em;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}
</style>