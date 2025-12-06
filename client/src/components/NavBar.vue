<template>
    <v-container class="navbar-border" fluid>
        <v-row>
          <v-btn to="/" text="Plan Bahn" variant="plain" class="planbahn-btn" />
        </v-row>
    </v-container>
</template>

<script setup>
  //
</script>

<style scoped>
.planbahn-btn {
  color: #EC0016 !important;
  font-weight: bold !important;
  font-size: 1.1rem;
}
 .navbar-border {
   border-bottom: 3px solid #EC0016;
   border-radius: 0 0 2px 2px;
 }
</style>