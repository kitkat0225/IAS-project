<template>
  <v-btn
    class="px-0"
    :class="active ? 'grey lighten-2' : ''"
    min-width="24"
    min-height="52"
    text
    :disabled="pDisabled"
    color="teal"
    @click="clicked"
  >
    <div class="my-2">
      <v-img
        style="margin: 0 auto"
        width="32"
        height="32"
        src="../../assets/images/object.png"
      />
      <div class="caption" :class="active ? 'font-weight-bold' : ''">
        {{ label }}
      </div>
    </div>
  </v-btn>
</template>

<script>
export default {
  name: "ObjectiveButton",

  props: {
    "label": {
      type: String,
      default: ""
    }, 
    "active": {
      type: Boolean,
      default: false
    }, 
    "pDisabled": {
      type: Boolean,
      default: false
    }},

  data: () => ({}),

  methods: {
    clicked: function() {
      this.$emit("click");
    }
  }
};
</script>
