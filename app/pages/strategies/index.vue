<template>
  <div class="page">
    <header class="head">
      <p class="spec">Catalogue</p>
      <h1 class="head-title">Strategies</h1>
      <p class="head-sub">
        Each one runs on its own timeframe and places orders on your behalf.
        Allocate capital to any of them, and withdraw whenever you like.
      </p>
    </header>

    <div class="tickrule tickrule--major" />

    <div v-if="!stgStore.strategies.length" class="empty">
      <p class="empty-lead">Nothing published yet.</p>
      <p class="empty-body">Strategies appear here once they are registered and active.</p>
    </div>

    <ul v-else class="list">
      <li v-for="strategy in stgStore.strategies" :key="strategy.id" class="row">
        <NuxtLink :to="`/strategies/${strategy.id}`" class="row-link">
          <div class="row-main">
            <h2 class="row-name">{{ strategy.name }}</h2>
            <p class="row-desc">{{ strategy.description || "No description." }}</p>
          </div>

          <dl class="row-stats">
            <div class="stat">
              <dt class="spec">Timeframe</dt>
              <dd class="figure stat-value">{{ strategy.run_tf || "—" }}</dd>
            </div>
            <div class="stat">
              <dt class="spec">Pool</dt>
              <dd class="figure stat-value">{{ formatCurrency(strategy.capital) }}</dd>
            </div>
            <div class="stat">
              <dt class="spec">Deployed</dt>
              <dd class="figure stat-value">
                {{ formatCurrency(strategy.capital_used) }}
              </dd>
            </div>
            <div class="stat">
              <dt class="spec">Unrealised</dt>
              <dd
                class="figure stat-value"
                :class="directionClass(strategy.unrealized_pnl)"
              >
                {{ formatSigned(strategy.unrealized_pnl) }}
              </dd>
            </div>
          </dl>
        </NuxtLink>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useStrategiesStore } from "@/store/strategy";

const stgStore = useStrategiesStore();

onMounted(async () => {
  if (!stgStore?.fetchStrategies) {
    return;
  }

  await stgStore.fetchStrategies();
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
  margin-bottom: 1rem;
  max-width: 44rem;
}

.head-title {
  font-size: clamp(1.75rem, 4vw, 2.5rem);
  margin: 0.375rem 0 0.75rem;
}

.head-sub {
  margin: 0;
  color: var(--text-muted);
}

.list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.row {
  border-bottom: 1px solid var(--rule);
}

.row-link {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1.5rem clamp(1.5rem, 4vw, 3rem);
  padding: 1.75rem 0;
  text-decoration: none;
  color: inherit;
  transition: background-color 0.15s ease, padding-left 0.15s ease;
}

.row-link:hover {
  background: var(--panel-raised);
  padding-left: 1rem;
}

.row-main {
  flex: 1 1 20rem;
  min-width: 0;
}

.row-name {
  font-size: 1.375rem;
}

.row-desc {
  margin: 0.4375rem 0 0;
  color: var(--text-muted);
  max-width: 38rem;
}

.row-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(5.5rem, auto));
  gap: clamp(1rem, 3vw, 2.25rem);
  margin: 0;
  text-align: right;
}

.stat dt {
  margin-bottom: 0.3125rem;
}

.stat-value {
  margin: 0;
  font-size: 1rem;
}

/* --- Empty --------------------------------------------------------------- */

.empty {
  padding: 4rem 0;
  max-width: 30rem;
}

.empty-lead {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 0.5rem;
}

.empty-body {
  margin: 0;
  color: var(--text-muted);
}

@media (max-width: 40rem) {
  .row-stats {
    grid-template-columns: repeat(2, 1fr);
    text-align: left;
    width: 100%;
  }
}
</style>
