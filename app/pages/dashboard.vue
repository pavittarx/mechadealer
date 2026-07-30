<template>
  <div class="page">
    <header class="head">
      <div>
        <p class="spec">Account</p>
        <h1 class="head-name">{{ userStore.name || "—" }}</h1>
      </div>
      <p class="spec head-meta">
        {{ userStore.strategies.length }}
        {{ userStore.strategies.length === 1 ? "position" : "positions" }}
      </p>
    </header>

    <div class="tickrule tickrule--major" />

    <!-- Capital is one quantity split two ways, so the total leads and the
         split sits under it rather than as three equal tiles. -->
    <section class="capital">
      <div>
        <p class="spec">Total capital</p>
        <p class="figure capital-total">{{ formatCurrency(totalCapital) }}</p>
      </div>

      <dl class="capital-split">
        <div>
          <dt class="spec">Allocated</dt>
          <dd class="figure capital-part">
            {{ formatCurrency(userStore.capital_used) }}
          </dd>
        </div>
        <div>
          <dt class="spec">Available</dt>
          <dd class="figure capital-part">
            {{ formatCurrency(userStore.capital) }}
          </dd>
        </div>
      </dl>
    </section>

    <section>
      <div class="section-head">
        <h2 class="section-title">Positions</h2>
        <NuxtLink to="/strategies" class="section-action">All strategies</NuxtLink>
      </div>

      <div v-if="!userStore.strategies.length" class="empty">
        <p class="empty-lead">No capital allocated.</p>
        <p class="empty-body">
          Pick a strategy and allocate to it. Orders are placed automatically
          while the market is open.
        </p>
        <NuxtLink to="/strategies" class="btn btn-primary">Browse strategies</NuxtLink>
      </div>

      <table v-else class="table">
        <thead>
          <tr>
            <th class="spec">Strategy</th>
            <th class="spec num">Allocated</th>
            <th class="spec num">Deployed</th>
            <th class="spec num">Unrealised</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="strategy in userStore.strategies" :key="strategy?.id || 0">
            <td>
              <NuxtLink :to="`/strategies/${strategy.id}`" class="table-link">
                {{ strategy.name }}
              </NuxtLink>
              <span v-if="strategy.run_tf" class="spec table-tf">{{
                strategy.run_tf
              }}</span>
            </td>
            <td class="figure num">{{ formatCurrency(strategy.capital) }}</td>
            <td class="figure num">{{ formatCurrency(strategy.capital_used) }}</td>
            <td class="figure num" :class="directionClass(strategy.unrealized_pnl)">
              {{ formatSigned(strategy.unrealized_pnl) }}
            </td>
          </tr>
        </tbody>
      </table>

      <p v-if="userStore.strategies.length && !hasFills" class="note">
        No fills yet, so unrealised P&amp;L is zero across the book. Strategies
        place orders between 09:15 and 15:30 IST on trading days.
      </p>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useUserStore } from "@/store/user";

const userStore = useUserStore();

/**
 * `capital` holds uninvested cash: allocating to a strategy decrements it, and
 * `capital_used` holds the allocated side. Showing `capital` alone as the total
 * made the figures fail to reconcile.
 */
const totalCapital = computed(
  () => Number(userStore.capital ?? 0) + Number(userStore.capital_used ?? 0),
);

const hasFills = computed(() =>
  userStore.strategies.some(
    (s: { capital_used?: number; unrealized_pnl?: number }) =>
      Number(s.capital_used ?? 0) !== 0 || Number(s.unrealized_pnl ?? 0) !== 0,
  ),
);

onMounted(async () => {
  if (!userStore?.userId || !userStore?.token) {
    navigateTo("/login");
    return;
  }

  await userStore.fetchUser();
  await userStore.fetchUserStrategies();
});

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
  align-items: flex-end;
  justify-content: space-between;
  gap: 1.5rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.head-name {
  font-size: clamp(1.75rem, 4vw, 2.5rem);
  margin-top: 0.375rem;
}

.head-meta {
  padding-bottom: 0.375rem;
}

/* --- Capital ------------------------------------------------------------- */

.capital {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: clamp(2rem, 6vw, 5rem);
  padding: 2.25rem 0 2.5rem;
}

.capital-total {
  margin: 0.5rem 0 0;
  font-size: clamp(2.75rem, 7vw, 4.25rem);
  font-weight: 500;
  line-height: 1;
}

.capital-split {
  display: flex;
  gap: clamp(1.5rem, 4vw, 3rem);
  margin: 0;
  padding-bottom: 0.5rem;
}

.capital-split dt {
  margin-bottom: 0.375rem;
}

.capital-part {
  margin: 0;
  font-size: 1.25rem;
  color: var(--text-muted);
}

/* --- Sections ------------------------------------------------------------ */

.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  padding-bottom: 0.875rem;
  border-bottom: 1px solid var(--rule-strong);
}

.section-title {
  font-size: 1.125rem;
}

.section-action {
  font-family: var(--font-data);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  text-decoration: none;
  border-bottom: 1px solid var(--rule-strong);
  padding-bottom: 2px;
}

.section-action:hover {
  color: var(--text);
  border-bottom-color: var(--ink);
}

/* --- Table --------------------------------------------------------------- */

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th,
.table td {
  padding: 0.9375rem 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--rule);
}

.table th {
  padding-top: 1rem;
  padding-bottom: 0.625rem;
  font-weight: 500;
}

.table th:first-child,
.table td:first-child {
  padding-left: 0;
}

.table th:last-child,
.table td:last-child {
  padding-right: 0;
}

.num {
  text-align: right;
}

.table-link {
  color: var(--text);
  text-decoration: none;
  font-weight: 500;
  border-bottom: 1px solid transparent;
}

.table-link:hover {
  border-bottom-color: var(--ink);
}

.table-tf {
  display: block;
  margin-top: 0.1875rem;
  font-size: 0.625rem;
}

/* --- Empty and notes ----------------------------------------------------- */

.empty {
  padding: 3.5rem 0 3rem;
  max-width: 30rem;
}

.empty-lead {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 0.5rem;
}

.empty-body {
  margin: 0 0 1.5rem;
  color: var(--text-muted);
}

.note {
  margin: 1.25rem 0 0;
  padding-left: 0.875rem;
  border-left: 2px solid var(--rule-strong);
  font-size: 0.875rem;
  color: var(--text-muted);
  max-width: 42rem;
}

@media (max-width: 40rem) {
  .table th:nth-child(3),
  .table td:nth-child(3) {
    display: none;
  }
}
</style>
