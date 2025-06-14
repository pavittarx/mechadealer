<template>
  <div class="page-container">
    <h1>All Available Strategies</h1>
    <p>This page will list all strategies available for investment.</p>
    <!-- Placeholder content -->
    <ul class="strategy-list">
      <li v-for="strategy in stgStore.strategies" :key="strategy.id">
        <NuxtLink :to="`/strategies/${strategy.id}`">
          <h2>{{ strategy.name }}</h2>
          <p>{{ strategy.description }}</p>

          <p>
            <strong>Capital Invested:</strong> {{ strategy.capital }}
          </p>
          <p>
            <strong>Capital (In Use):</strong> {{ strategy.capital_used }}
          </p>
          <p>
            <strong>Unrealized Pnl:</strong> {{ strategy.unrealized_pnl }}
          </p>

        </NuxtLink>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useStrategiesStore } from '@/store/strategy';

const stgStore = useStrategiesStore();

onMounted(async () => {
  if (!stgStore?.fetchStrategies) {
    return
  }

  await stgStore.fetchStrategies();
});

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
  /* Add margin if main-content doesn't have padding */
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

h1 {
  font-size: 2em;
  color: #1A237E;
  /* Deep Indigo */
  margin-bottom: 20px;
}

p {
  font-size: 1.1em;
  color: #555;
  margin-bottom: 20px;
}

.strategy-list {
  list-style: none;
  padding: 0;
}

.strategy-list li {
  background-color: #f9f9f9;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  margin-bottom: 15px;
  transition: box-shadow 0.2s ease;
}

.strategy-list li a {
  display: block;
  padding: 20px;
  text-decoration: none;
  color: inherit;
}

.strategy-list li:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.strategy-list h2 {
  font-size: 1.5em;
  color: #283593;
  /* Indigo */
  margin-bottom: 8px;
}

.strategy-list p {
  font-size: 1em;
  color: #666;
  margin-bottom: 5px;
}
</style>