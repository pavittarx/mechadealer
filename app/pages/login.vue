<template>
  <div class="page">
    <!-- Left plate carries the identity so the form stays uncluttered. -->
    <section class="plate">
      <NuxtLink to="/" class="plate-mark display">mechadealer</NuxtLink>
      <div class="tickrule tickrule--inverse plate-scale" />
      <p class="plate-line">
        Automated strategies on NSE and BSE. You allocate the capital, the
        machine places the orders.
      </p>
      <p class="spec plate-foot">Market 09:15–15:30 IST</p>
    </section>

    <section class="form-side">
      <div class="form-wrap">
        <p class="spec">Sign in</p>
        <h1 class="form-title">Your account</h1>

        <form class="form" novalidate @submit.prevent="handleLogin">
          <div class="field">
            <label for="username" class="spec">Username</label>
            <input
              id="username"
              v-model="username"
              class="input"
              type="text"
              autocomplete="username"
              required
            >
          </div>

          <div class="field">
            <label for="password" class="spec">Password</label>
            <input
              id="password"
              v-model="password"
              class="input"
              type="password"
              autocomplete="current-password"
              required
            >
          </div>

          <p v-if="error" class="error" role="alert">{{ error }}</p>

          <button type="submit" class="btn btn-primary submit" :disabled="pending">
            {{ pending ? "Signing in…" : "Sign in" }}
          </button>
        </form>

        <p class="alt">
          Try it with the demo account:
          <span class="figure alt-creds">demo / demo1234</span>
        </p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";

const username = ref("");
const password = ref("");
const error = ref("");
const pending = ref(false);

type LoginResponse = {
  is_error: boolean;
  is_success: boolean;
  message: string;
  data: {
    user_id: number;
    token: string;
  } | null;
};

const handleLogin = async () => {
  const runtimeConfig = useRuntimeConfig();
  const url = runtimeConfig.public.baseUrl + "/login";

  error.value = "";
  pending.value = true;

  try {
    const res: LoginResponse = await $fetch(url, {
      method: "POST",
      body: {
        username: username.value,
        password: password.value,
      },
    });

    // The API answers 200 with is_error set. Without returning here the next
    // line read user_id off a null body and threw, so a wrong password looked
    // like nothing happening at all.
    if (res.is_error || !res.data) {
      error.value = res.message || "Those details did not match an account.";
      return;
    }

    const userStore = useUserStore();
    userStore.setUserId(res.data.user_id);
    userStore.setToken(res.data.token);

    navigateTo("/dashboard");
  } catch (e) {
    console.error(e);
    error.value = "Could not reach the server. Try again in a moment.";
  } finally {
    pending.value = false;
  }
};

definePageMeta({
  layout: "default",
});
</script>

<style scoped>
.page {
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 100vh;
}

/* --- Identity plate ------------------------------------------------------ */

.plate {
  display: flex;
  flex-direction: column;
  padding: clamp(2rem, 5vw, 3.5rem);
  background: var(--ink);
  color: var(--text-inverse);
}

.plate-mark {
  font-size: clamp(1.5rem, 3vw, 2rem);
  color: var(--text-inverse);
  text-decoration: none;
}

.plate-scale {
  margin: 1.5rem 0 auto;
}

.plate-line {
  margin: 0;
  max-width: 24rem;
  font-size: clamp(1.125rem, 2.2vw, 1.5rem);
  line-height: 1.4;
  color: var(--text-inverse);
}

.plate-foot {
  margin: 2rem 0 0;
  color: var(--text-inverse-muted);
}

/* --- Form ---------------------------------------------------------------- */

.form-side {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: clamp(2rem, 5vw, 3.5rem);
}

.form-wrap {
  width: 100%;
  max-width: 22rem;
}

.form-title {
  font-size: 1.875rem;
  margin: 0.375rem 0 2rem;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.4375rem;
}

.submit {
  margin-top: 0.25rem;
  width: 100%;
}

.error {
  margin: 0;
  padding-left: 0.75rem;
  border-left: 2px solid var(--short);
  color: var(--short);
  font-size: 0.875rem;
}

.alt {
  margin: 2rem 0 0;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.alt-creds {
  color: var(--text);
}

@media (max-width: 52rem) {
  .page {
    grid-template-columns: 1fr;
  }

  .plate {
    padding-bottom: 2rem;
  }

  .plate-scale {
    margin-bottom: 1.5rem;
  }

  .plate-foot {
    display: none;
  }
}
</style>
