<script setup lang="ts">
</script>

<template>
  <div class="page">
    <router-view />
  </div>
</template>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 24px;

}
/* Цвета для рисков */
[data-risk="high"] {
  background: rgba(255, 79, 79, 0.1);
  color: #ff4f4f;
  border: 1px solid rgba(255, 79, 79, 0.3);
}

[data-risk="medium"] {
  background: rgba(255, 184, 79, 0.1);
  color: #ffb84f;
  border: 1px solid rgba(255, 184, 79, 0.3);
}

[data-risk="low"] {
  background: rgba(79, 255, 138, 0.1);
  color: #4fff8a;
  border: 1px solid rgba(79, 255, 138, 0.3);
}

.risk {
  padding: 4px 12px;
  border-radius: 99px;
  font-size: 0.8rem;
  font-weight: 600;
}
</style>