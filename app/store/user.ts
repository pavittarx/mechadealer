export const useUserStore = defineStore("userStore", {
  state: () => ({
    userId: -1,
    token: "",
  }),
  actions: {
    setUserId(userId: number) {
      this.userId = userId;
    },
    setToken(token: string) {
      this.token = token;
    },
    async fetchUser() {
      if (!this.userId) {
        console.error("Unable to fetch user, UserId not present.");
        return;
      }

      const url = process.env.BASE_URL + "/user/" + this.userId;
      const res = await $fetch(url);
    },
  },
  persist: {
    storage: import.meta.client && localStorage ? localStorage : undefined,
    pick: ["userId", "token"],
  },
});
