<template>
    <router-view/>
</template>

<script>
import { useRouter } from 'vue-router';

export default {
  mounted() {
    const router = useRouter();
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
    }
  }
}
</script>

