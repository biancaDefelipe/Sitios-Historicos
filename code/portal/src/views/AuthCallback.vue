<script setup>
import { useAuthStore } from '../stores/authStore'
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

onMounted(async () => {
  const code = route.query.code
  const state = route.query.state 

  if (code) {
    try {
      await auth.handleGoogleCallback(code.toString())

      const returnTo = state || sessionStorage.getItem("auth.returnTo") || '/'


      sessionStorage.removeItem("auth.returnTo")

      router.replace(returnTo)

    } catch (err) {
      router.replace({ name: 'home' })
    }

  } else {
    router.replace({ name: 'home' })
  }
})
</script>
