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
        <button v-if="!hasInvestment" class="btn btn-primary" @click="investInStrategy">
          Invest Now
        </button>
        <button v-else class="btn btn-outline" @click="modifyInvestment">
          Modify Investment
        </button>
      </div>
    </div>

    <div v-else>
      <p>Loading strategy details or strategy not found...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
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

const hasInvestment = ref(false); // This should be determined by API call

const investInStrategy = () => {
  alert(`Investing in ${strategy.value?.name}... (Placeholder)`);
  // API call to invest
};

const modifyInvestment = () => {
  alert(`Modifying investment in ${strategy.value?.name}... (Placeholder)`);
  // Navigate to a modification page or open a modal
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
  /* Deep Indigo */
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
  /* Indigo */
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
  /* Amber */
  color: #333;
  font-weight: bold;
}

.btn-primary:hover {
  background-color: #FFB300;
  /* Darker Amber */
}

.btn-secondary {
  background-color: #3949AB;
  /* Indigo */
  color: white;
}

.btn-secondary:hover {
  background-color: #283593;
}

.btn-outline {
  background-color: transparent;
  border-color: #3949AB;
  color: #3949AB;
}

.btn-outline:hover {
  background-color: #e8eaf6;
  /* Light Indigo */
}
</style>