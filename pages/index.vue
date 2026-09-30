<script setup lang="ts">
const { init } = useSmoothScroll()
onMounted(() => init())
</script>

<template>
  <main class="page">
    <TheHeader />
    <SectionHero />
    <SectionMoments />
    <SectionIcons />
    <SectionLookCloser />
    <SectionTime />
    <SectionStories />
    <SectionFeatured />
    <SectionToday />
    <SectionYourMoment />
    <SectionNews />
    <TheFooter />
  </main>
</template>

<style scoped>
.page {
  position: relative;
  overflow: clip;
}
</style>
