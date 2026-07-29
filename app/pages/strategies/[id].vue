<template>
  <div class="page">
    <template v-if="strategy">
      <header class="head">
        <div>
          <NuxtLink to="/strategies" class="spec back">← All strategies</NuxtLink>
          <h1 class="head-title">{{ strategy.name }}</h1>
          <p class="head-desc">{{ strategy.description || "No description." }}</p>
        </div>

        <div class="badges">
          <span class="badge" :class="strategy.is_active ? 'badge--on' : 'badge--off'">
            {{ strategy.is_active ? "Running" : "Stopped" }}
          </span>
          <span class="badge">{{ strategy.run_tf }}</span>
        </div>
      </header>

      <div class="tickrule tickrule--major" />

      <section class="block">
        <h2 class="spec block-title">Capital</h2>
        <dl class="grid">
          <div class="cell">
            <dt class="spec">Pool</dt>
            <dd class="figure cell-value">{{ formatCurrency(strategy.capital) }}</dd>
          </div>
          <div class="cell">
            <dt class="spec">Deployed</dt>
            <dd class="figure cell-value">
              {{ formatCurrency(strategy.capital_used) }}
            </dd>
          </div>
          <div class="cell">
            <dt class="spec">Units issued</dt>
            <dd class="figure cell-value">{{ formatUnits(strategy.units) }}</dd>
          </div>
        </dl>
      </section>

      <section class="block">
        <h2 class="spec block-title">Performance</h2>
        <dl class="grid">
          <div class="cell">
            <dt class="spec">Realised</dt>
            <dd class="figure cell-value" :class="directionClass(strategy.pnl)">
              {{ formatSigned(strategy.pnl) }}
            </dd>
          </div>
          <div class="cell">
            <dt class="spec">Unrealised</dt>
            <dd
              class="figure cell-value"
              :class="directionClass(strategy.unrealized_pnl)"
            >
              {{ formatSigned(strategy.unrealized_pnl) }}
            </dd>
          </div>
          <div class="cell">
            <dt class="spec">Unit price</dt>
            <dd class="figure cell-value">{{ unitPrice }}</dd>
          </div>
          <div class="cell">
            <dt class="spec">Live since</dt>
            <dd class="figure cell-value">{{ liveSince }}</dd>
          </div>
        </dl>

        <p v-if="!hasFills" class="note">
          No fills recorded yet, so both figures are zero. This strategy places
          orders on {{ strategy.run_tf }} bars between 09:15 and 15:30 IST.
        </p>
      </section>

      <div class="actions">
        <button class="btn btn-primary" @click="openInvestDialog">Allocate</button>
        <button class="btn btn-outline" @click="openWithdrawDialog">Withdraw</button>
      </div>
    </template>

    <p v-else class="loading">Loading strategy…</p>

    <!-- Allocate -->
    <dialog ref="investDialog" class="dialog" @close="resetInvest">
      <form class="dialog-body" method="dialog" @submit.prevent="confirmInvestment">
        <h2 class="dialog-title">Allocate to {{ strategy?.name }}</h2>
        <p class="dialog-sub">
          You are issued units at the strategy's current price.
        </p>

        <div class="field">
          <label for="investAmount" class="spec">Amount (₹)</label>
          <input
            id="investAmount"
            v-model.number="investAmount"
            class="input"
            type="number"
            min="1"
            step="1"
          >
        </div>

        <p v-if="investError" class="error" role="alert">{{ investError }}</p>

        <div class="dialog-actions">
          <button type="button" class="btn btn-outline" @click="closeInvestDialog">
            Cancel
          </button>
          <button type="submit" class="btn btn-primary" :disabled="investPending">
            {{ investPending ? "Allocating…" : "Allocate" }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- Withdraw -->
    <dialog ref="withdrawDialog" class="dialog" @close="resetWithdraw">
      <form class="dialog-body" method="dialog" @submit.prevent="confirmWithdrawal">
        <h2 class="dialog-title">Withdraw from {{ strategy?.name }}</h2>
        <p class="dialog-sub">Units are redeemed at the strategy's current price.</p>

        <div class="field">
          <label for="withdrawAmount" class="spec">Amount (₹)</label>
          <input
            id="withdrawAmount"
            v-model.number="withdrawAmount"
            class="input"
            type="number"
            min="1"
            step="1"
            :max="strategy?.capital || 0"
          >
        </div>

        <p v-if="withdrawError" class="error" role="alert">{{ withdrawError }}</p>

        <div class="dialog-actions">
          <button type="button" class="btn btn-outline" @click="closeWithdrawDialog">
            Cancel
          </button>
          <button type="submit" class="btn btn-primary" :disabled="withdrawPending">
            {{ withdrawPending ? "Withdrawing…" : "Withdraw" }}
          </button>
        </div>
      </form>
    </dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { useUserStore } from "~/store/user";

const route = useRoute();
const userStore = useUserStore();
const strategyId = computed(() => route.params.id as string)?.value;

interface Strategy {
  id: number;
  name: string;
  run_tf: string;
  description: string;
  capital: number;
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
const investError = ref("");
const withdrawError = ref("");
const investPending = ref(false);
const withdrawPending = ref(false);

const hasFills = computed(
  () =>
    Number(strategy.value?.capital_used ?? 0) !== 0 ||
    Number(strategy.value?.pnl ?? 0) !== 0 ||
    Number(strategy.value?.unrealized_pnl ?? 0) !== 0,
);

/** Capital per unit. Undefined before anyone has allocated. */
const unitPrice = computed(() => {
  const units = Number(strategy.value?.units ?? 0);
  if (!units) return "—";
  return formatCurrency(Number(strategy.value?.capital ?? 0) / units);
});

const liveSince = computed(() => {
  const created = strategy.value?.created_at;
  if (!created) return "—";
  return new Date(created).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
});

async function fetchStrategyById(id: number) {
  const runtimeConfig = useRuntimeConfig();
  const baseUrl = runtimeConfig.public.baseUrl;

  try {
    const res: StrategyRes = await $fetch(`${baseUrl}/strategies/${id}`, {
      method: "GET",
    });

    if (res.is_error) {
      throw new Error(res.message || "Could not load this strategy");
    }

    return res.data as Strategy;
  } catch (error) {
    console.error("Error fetching strategy:", error);
  }
}

onMounted(async () => {
  strategy.value = await fetchStrategyById(parseInt(strategyId));
});

const openInvestDialog = () => investDialog.value?.showModal();
const closeInvestDialog = () => investDialog.value?.close();
const openWithdrawDialog = () => withdrawDialog.value?.showModal();
const closeWithdrawDialog = () => withdrawDialog.value?.close();

const resetInvest = () => {
  investAmount.value = 0;
  investError.value = "";
};

const resetWithdraw = () => {
  withdrawAmount.value = 0;
  withdrawError.value = "";
};

async function move(path: string, amount: number) {
  const runtimeConfig = useRuntimeConfig();
  const res: StrategyRes = await $fetch(
    `${runtimeConfig.public.baseUrl}${path}`,
    {
      method: "POST",
      body: { strategy_id: parseInt(strategyId), amount },
      headers: { Authorization: `Bearer ${userStore.token}` },
    },
  );

  if (res.is_error) {
    throw new Error(res.message || "That did not go through");
  }

  strategy.value = await fetchStrategyById(parseInt(strategyId));
  await userStore.fetchUser();
  await userStore.fetchUserStrategies();
}

// Failures used to reach the console only, so the dialog just sat there.
const confirmInvestment = async () => {
  investError.value = "";

  if (!investAmount.value || investAmount.value <= 0) {
    investError.value = "Enter an amount greater than zero.";
    return;
  }

  investPending.value = true;
  try {
    await move("/strategies/invest", investAmount.value);
    closeInvestDialog();
  } catch (e) {
    investError.value = (e as Error).message;
  } finally {
    investPending.value = false;
  }
};

const confirmWithdrawal = async () => {
  withdrawError.value = "";

  if (!withdrawAmount.value || withdrawAmount.value <= 0) {
    withdrawError.value = "Enter an amount greater than zero.";
    return;
  }

  withdrawPending.value = true;
  try {
    await move("/strategies/withdraw", withdrawAmount.value);
    closeWithdrawDialog();
  } catch (e) {
    withdrawError.value = (e as Error).message;
  } finally {
    withdrawPending.value = false;
  }
};

definePageMeta({
  layout: "default",
});
</script>

<style scoped>
.page {
  max-width: var(--max);
  margin: 0 auto;
  padding: clamp(1.75rem, 4vw, 3rem) var(--gutter) 4rem;
}

.head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1.5rem;
  flex-wrap: wrap;
  margin-bottom: 1.25rem;
}

.back {
  display: inline-block;
  margin-bottom: 0.875rem;
  color: var(--text-muted);
  text-decoration: none;
}

.back:hover {
  color: var(--text);
}

.head-title {
  font-size: clamp(1.75rem, 4vw, 2.5rem);
}

.head-desc {
  margin: 0.625rem 0 0;
  color: var(--text-muted);
  max-width: 44rem;
}

.badges {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.badge {
  font-family: var(--font-data);
  font-size: 0.6875rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  padding: 0.3125rem 0.625rem;
  border: 1px solid var(--rule-strong);
  border-radius: 2px;
  color: var(--text-muted);
}

.badge--on {
  border-color: var(--long);
  color: var(--long);
}

.badge--off {
  border-color: var(--rule-strong);
}

/* --- Blocks -------------------------------------------------------------- */

.block {
  padding: 2.25rem 0 0;
}

.block-title {
  margin: 0 0 1.25rem;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(9rem, 1fr));
  gap: 1.75rem clamp(1.5rem, 4vw, 3rem);
  margin: 0;
}

.cell dt {
  margin-bottom: 0.4375rem;
}

.cell-value {
  margin: 0;
  font-size: clamp(1.25rem, 2.5vw, 1.625rem);
  font-weight: 500;
}

.note {
  margin: 1.75rem 0 0;
  padding-left: 0.875rem;
  border-left: 2px solid var(--rule-strong);
  font-size: 0.875rem;
  color: var(--text-muted);
  max-width: 42rem;
}

.actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid var(--rule-strong);
}

.loading {
  padding: 4rem 0;
  color: var(--text-muted);
}

/* --- Dialog -------------------------------------------------------------- */

.dialog {
  border: 1px solid var(--rule-strong);
  border-radius: 2px;
  background: var(--panel-raised);
  color: var(--text);
  padding: 0;
  max-width: 26rem;
  width: calc(100% - 2rem);
}

.dialog::backdrop {
  background: rgba(21, 24, 27, 0.55);
}

.dialog-body {
  padding: 1.75rem;
}

.dialog-title {
  font-size: 1.25rem;
}

.dialog-sub {
  margin: 0.5rem 0 1.5rem;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.4375rem;
}

.error {
  margin: 1rem 0 0;
  padding-left: 0.75rem;
  border-left: 2px solid var(--short);
  color: var(--short);
  font-size: 0.875rem;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.75rem;
}
</style>
