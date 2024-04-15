<template>
  <div>

    <h1 style="text-align: center">Edit Pet Profile</h1>
    <hr class="left-align-hr">

    <div class="container mt-5">
      <form @submit.prevent="submitForm" enctype="multipart/form-data">
        <div v-for="field in formFields" :key="field.name">
          <label :for="field.name">{{ field.label }}</label>
          <input :type="field.type" :id="field.name" :name="field.name" v-model="field.value" />
        </div>
        <div class="row justify-content-center">
          <div class="col-auto">
            <button type="submit" class="btn btn-primary">Save changes</button>
          </div>
          <div class="col-auto">
            <a :href="cancelUrl" class="btn btn-primary">Cancel</a>
          </div>
        </div>
      </form>
    </div>
    <br>
  </div>
</template>

<script>
export default {
  name: 'EditPetProfileComponent',
  data() {
    return {
      formFields: [
        { name: 'name', label: 'Pet Name', type: 'text', value: 'Fluffy' },
        { name: 'age', label: 'Age', type: 'number', value: 3 },
        { name: 'breed', label: 'Breed', type: 'text', value: 'Golden Retriever' },
        // Add additional fields as needed
      ],
      cancelUrl: '/pet/profile'  // Assuming this URL is managed by your Vue router
    }
  },
  methods: {
    submitForm() {
      console.log("Form submitted with:", this.formFields);
      // Implement form submission logic, e.g., making an API call
    }
  }
}
</script>

<style scoped>
      .left-align-hr {
        width: calc(500% + 200px);
        margin: 0 -50px 50px -500px;
        border: none;
        border-top: 3px dotted darkblue;
        border-radius: 5px;
      }
</style>
