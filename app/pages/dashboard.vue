<template>
  <div class="dashboard-page-wrapper">
    <div class="dashboard-container">
      <header class="dashboard-header">
        <h1>User Dashboard</h1>
        <div class="user-details">
          <p><strong>User:</strong> {{ userData.name }} ({{ userData.email }})</p>
        </div>
      </header>

      <section class="capital-summary-section">
        <h2>Capital Overview</h2>
        <div class="capital-grid">
          <div class="capital-item">
            <span class="label">Total Capital</span>
            <span class="value">{{ formatCurrency(capitalData.totalCapital) }}</span>
          </div>
          <div class="capital-item">
            <span class="label">Invested in Strategies</span>
            <span class="value">{{ formatCurrency(capitalData.investedInStrategies) }}</span>
          </div>
          <div class="capital-item">
            <span class="label">Available Capital</span>
            <span class="value">{{ formatCurrency(capitalData.availableCapital) }}</span>
          </div>
          <div class="capital-item">
            <span class="label">Unrealized P&L</span>
            <span class="value" :class="pnlClass(capitalData.unrealizedPnl)">{{
              formatCurrency(capitalData.unrealizedPnl) }}</span>
          </div>
        </div>
      </section>

      <section class="holdings-section">
        <h2>Holdings (Invested Strategies)</h2>
        <div v-if="holdingsData.length === 0" class="no-holdings">
          <p>No strategies invested in yet.</p>
        </div>
        <div v-else class="holdings-list">
          <div v-for="holding in holdingsData" :key="holding.id" class="holding-item">
            <h3>{{ holding.name }}</h3>
            <p><strong>Invested:</strong> {{ formatCurrency(holding.investedAmount) }}</p>
            <p><strong>Current Value:</strong> {{ formatCurrency(holding.currentValue) }}</p>
            <p><strong>P&L:</strong> <span :class="pnlClass(holding.pnl)">{{ formatCurrency(holding.pnl) }}</span></p>
            <p><strong>Strategy Type:</strong> {{ holding.type }}</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useUserStore } from "@/store/user";

// --- Mock Data ---
// In a real application, this data would be fetched from an API
const userData = ref({
  name: 'John Doe',
  email: 'john.doe@example.com',
  userId: 'user123'
});

const capitalData = ref({
  totalCapital: 100000,
  investedInStrategies: 65000,
  availableCapital: 35000,
  unrealizedPnl: 5250.75
});

const holdingsData = ref([
  {
    id: 'strategy001',
    name: 'Aggressive Growth Alpha',
    investedAmount: 25000,
    currentValue: 27500,
    pnl: 2500,
    type: 'Equity Momentum'
  },
  {
    id: 'strategy002',
    name: 'Stable Income Beta',
    investedAmount: 30000,
    currentValue: 31500.75,
    pnl: 1500.75,
    type: 'Fixed Income Arbitrage'
  },
  {
    id: 'strategy003',
    name: 'Tech Opportunities Gamma',
    investedAmount: 10000,
    currentValue: 11250,
    pnl: 1250,
    type: 'Long/Short Tech Sector'
  }
]);

// --- End Mock Data ---

const userStore = useUserStore();

onMounted(async () => {
  console.log("Mounted");

  if (!userStore?.userId || !userStore?.token) {
    console.log("User not logged in, redirecting to login page.");
    navigateTo('/login');
    return;
  }

})


const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
};

const pnlClass = (pnl: number) => {
  if (pnl > 0) return 'pnl-positive';
  if (pnl < 0) return 'pnl-negative';
  return 'pnl-neutral';
};



definePageMeta({
  layout: 'default'
});
</script>

<style scoped>
.dashboard-page-wrapper {
  display: flex;
  justify-content: center;
  padding: 20px;
  background-color: #f0f2f5;
  /* Light grey background */
  min-height: 100vh;
  font-family: 'Roboto', 'Arial', sans-serif;
}

.dashboard-container {
  width: 100%;
  max-width: 1200px;
  background-color: #ffffff;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.dashboard-header {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.dashboard-header h1 {
  font-size: 2.2em;
  color: #1A237E;
  /* Deep Indigo */
  margin-bottom: 5px;
}

.user-details p {
  font-size: 1em;
  color: #555;
}

.capital-summary-section,
.holdings-section {
  margin-bottom: 30px;
}

.capital-summary-section h2,
.holdings-section h2 {
  font-size: 1.8em;
  color: #283593;
  /* Indigo */
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.capital-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.capital-item {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
}

.capital-item .label {
  font-size: 0.9em;
  color: #666;
  margin-bottom: 8px;
  font-weight: 500;
}

.capital-item .value {
  font-size: 1.5em;
  font-weight: bold;
  color: #333;
}

.pnl-positive {
  color: #2E7D32;
  /* Green */
}

.pnl-negative {
  color: #C62828;
  /* Red */
}

.pnl-neutral {
  color: #555;
  /* Grey for neutral P&L */
}

.no-holdings {
  text-align: center;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  color: #777;
}

.holdings-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.holding-item {
  background-color: #ffffff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.07);
  border: 1px solid #e8e8e8;
}

.holding-item h3 {
  font-size: 1.3em;
  color: #3949AB;
  /* Indigo */
  margin-bottom: 10px;
}

.holding-item p {
  font-size: 0.95em;
  color: #444;
  margin-bottom: 6px;
  line-height: 1.5;
}

.holding-item p strong {
  color: #222;
}
</style>