<script setup lang="ts">
import { news } from '~/data/content'
</script>

<template>
  <section id="news" class="news section container">
    <div class="section-head news__head">
      <span class="kicker">10 — News / Notice</span>
      <h2 class="en-display size-xl">News</h2>
    </div>
    <ul class="news__list">
      <li v-for="(n, i) in news" :key="i">
        <a href="#" class="news__row" @click.prevent>
          <span class="news__cat en-display">{{ n.cat }}</span>
          <span class="news__title body-l">{{ n.title }}</span>
          <span class="news__date body-m">{{ n.date }}</span>
          <span class="news__arrow" aria-hidden="true">→</span>
        </a>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.news {
  background: var(--cream);
}
.news__list {
  list-style: none;
  margin: 0;
  padding: 0;
  border-top: var(--stroke) solid var(--ink);
}
.news__row {
  display: grid;
  grid-template-columns: 8em 1fr auto 2em;
  align-items: center;
  gap: 20px;
  padding: 22px 8px;
  border-bottom: var(--stroke) solid var(--ink);
  transition: background-color 0.2s, padding 0.3s;
}
.news__row:hover {
  background: var(--banana);
  padding-inline: 20px;
}
.news__cat {
  justify-self: start;
  padding: 4px 10px;
  border: 2px solid var(--ink);
  border-radius: 999px;
  font-size: 13px;
  letter-spacing: 0.06em;
}
.news__date {
  opacity: 0.6;
}
.news__arrow {
  font-size: 22px;
  font-weight: 700;
}
@media (max-width: 700px) {
  .news__row {
    grid-template-columns: 1fr auto;
  }
  .news__title {
    grid-column: 1 / -1;
    grid-row: 2;
  }
  .news__arrow {
    display: none;
  }
}
</style>
