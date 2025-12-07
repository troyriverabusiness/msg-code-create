<template>
    <v-container class="navbar-border" fluid>
        <v-row class="navbar-row" align="center">
          <RouterLink to="/" class="logo-link">
            <img :src="pb_logo" alt="Plan Bahn" class="logo-img" />
          </RouterLink>
          <span class="navbar-text">Bahn fahren, aber smart.</span>
          <v-spacer />
          <v-btn prepend-icon="mdi-account-circle" to="/login" variant="text" class="login-btn">Anmelden</v-btn>
        </v-row>
    </v-container>
</template>

<script setup>
import pb_logo from '@/assets/pb.png'
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

.navbar-row {
  gap: 10px;
}

.navbar-text {
  color: #535050;
  font-weight: 600;
  font-size: 1rem;
}

.login-btn {
  color: #1f1f1f;
  font-weight: 600;
  text-transform: none;
}

.logo-link {
  display: inline-flex;
  align-items: center;
  margin-left: 8px;
}

.logo-img {
  height: 45px;
  width: auto;
  display: block;
}
</style>