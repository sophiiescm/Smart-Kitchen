<script lang="ts">
async function register(username: string, email: string, password: string) {
  const response = await fetch('http://localhost:8000/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password })
  });
  return response.json();
}
</script>

<div class="register-container">
  <p>Registrierungsseite</p>
</div>
