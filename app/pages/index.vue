<template>
  <div class="landing-container">
    <header class="hero-section">
      <img src="/" alt="Mechadealer Logo" class="logo" />
      <h1>Welcome to Mechadealer</h1>
      <p class="subtitle">Empowering Retail Investors with Automated Trading Strategies</p>
      <NuxtLink to="/login" class="cta-button">Login to Access Strategies</NuxtLink>
    </header>

    <section class="features-section">
      <h2>Unlock Your Investment Potential</h2>
      <div class="features-grid">
        <div class="feature-item">
          <Icon name="uil:chart-line" class="feature-icon" />
          <h3>Automated Strategies</h3>
          <p>Invest in a diverse range of professionally managed automated trading strategies.</p>
        </div>
        <div class="feature-item">
          <Icon name="uil:monitor-heart-rate" class="feature-icon" />
          <h3>Performance Metrics</h3>
          <p>View key performance indicators and track the historical success of each strategy.</p>
        </div>
        <div class="feature-item">
          <Icon name="uil:clock-eight" class="feature-icon" />
          <h3>Real-Time Monitoring</h3>
          <p>Monitor your investments and adjust your portfolio in real-time.</p>
        </div>
         <div class="feature-item">
          <Icon name="uil:shield-check" class="feature-icon" />
          <h3>Secure Platform</h3>
          <p>Invest with confidence on our secure and reliable trading platform.</p>
        </div>
      </div>
    </section>

    <section class="how-it-works-section">
      <h2>How It Works</h2>
      <div class="steps-container">
        <div class="step-item">
          <div class="step-number">1</div>
          <h3>Sign Up</h3>
          <p>Create your account in minutes and get verified.</p>
        </div>
        <div class="step-item">
          <div class="step-number">2</div>
          <h3>Explore Strategies</h3>
          <p>Browse our curated list of automated trading strategies.</p>
        </div>
        <div class="step-item">
          <div class="step-number">3</div>
          <h3>Invest</h3>
          <p>Choose your strategies and allocate your investment funds.</p>
        </div>
        <div class="step-item">
          <div class="step-number">4</div>
          <h3>Monitor & Adjust</h3>
          <p>Track performance and manage your investments on the go.</p>
        </div>
      </div>
    </section>

    <footer class="footer-section">
      <p>&copy; {{ new Date().getFullYear() }} Mechadealer. All rights reserved.</p>
      <nav>
        <NuxtLink to="/about">About Us</NuxtLink> |
        <NuxtLink to="/strategies">Strategies</NuxtLink> |
        <NuxtLink to="/contact">Contact</NuxtLink> |
        <NuxtLink to="/privacy">Privacy Policy</NuxtLink>
      </nav>
    </footer>
  </div>
</template>

<script setup lang="ts">
// Using Nuxt Icon for feature icons, ensure @nuxt/icon module is installed and configured.
</script>

<style scoped>
.landing-container {
  font-family: 'Roboto', 'Arial', sans-serif;
  color: #333;
  line-height: 1.6;
}

.hero-section {
  background: linear-gradient(135deg, #1A237E 0%, #283593 50%, #3949AB 100%); /* Deep Indigo to Indigo */
  color: white;
  padding: 80px 20px;
  text-align: center;
}

.logo {
  max-width: 180px;
  margin-bottom: 25px;
}

.hero-section h1 {
  font-size: 3em;
  margin-bottom: 15px;
  font-weight: 700;
}

.subtitle {
  font-size: 1.3em;
  margin-bottom: 35px;
  opacity: 0.9;
  font-weight: 300;
}

.cta-button {
  background-color: #FFC107; /* Amber */
  color: #333;
  padding: 15px 35px;
  text-decoration: none;
  border-radius: 25px;
  font-size: 1.1em;
  font-weight: bold;
  transition: background-color 0.3s ease, transform 0.2s ease;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.cta-button:hover {
  background-color: #FFB300; /* Darker Amber */
  transform: translateY(-2px);
}

.features-section {
  padding: 60px 20px;
  text-align: center;
  background-color: #f4f6f8;
}

.features-section h2 {
  font-size: 2.2em;
  margin-bottom: 50px;
  color: #1A237E; /* Deep Indigo */
  font-weight: 600;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 30px;
  max-width: 1200px;
  margin: 0 auto;
}

.feature-item {
  background-color: #ffffff;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.08);
  transition: transform 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-5px);
}

.feature-icon {
  font-size: 3.5em;
  color: #3949AB; /* Indigo */
  margin-bottom: 20px;
}

.feature-item h3 {
  font-size: 1.6em;
  margin-bottom: 10px;
  color: #333;
  font-weight: 500;
}

.feature-item p {
  font-size: 1em;
  color: #555;
}

.how-it-works-section {
  padding: 60px 20px;
  text-align: center;
}

.how-it-works-section h2 {
  font-size: 2.2em;
  margin-bottom: 50px;
  color: #1A237E; /* Deep Indigo */
  font-weight: 600;
}

.steps-container {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  max-width: 1200px;
  margin: 0 auto;
}

.step-item {
  flex-basis: calc(25% - 20px);
  margin-bottom: 30px;
  padding: 20px;
  text-align: center;
}

.step-number {
  width: 50px;
  height: 50px;
  line-height: 50px;
  border-radius: 50%;
  background-color: #FFC107; /* Amber */
  color: #333;
  font-size: 1.5em;
  font-weight: bold;
  margin: 0 auto 15px auto;
}

.step-item h3 {
  font-size: 1.4em;
  margin-bottom: 10px;
  color: #333;
  font-weight: 500;
}

.step-item p {
  font-size: 0.95em;
  color: #555;
}

.footer-section {
  background-color: #263238; /* Blue Grey Darken-3 */
  color: #CFD8DC; /* Blue Grey Lighten-4 */
  text-align: center;
  padding: 30px 20px;
  font-size: 0.9em;
}

.footer-section nav a {
  color: #FFC107; /* Amber */
  margin: 0 15px;
  text-decoration: none;
  transition: color 0.3s ease;
}

.footer-section nav a:hover {
  color: #FFA000; /* Darker Amber */
  text-decoration: underline;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .hero-section h1 {
    font-size: 2.5em;
  }
  .subtitle {
    font-size: 1.1em;
  }
  .features-grid {
    grid-template-columns: 1fr;
  }
  .step-item {
    flex-basis: calc(50% - 20px);
  }
}

@media (max-width: 480px) {
  .step-item {
    flex-basis: 100%;
  }
}
</style>