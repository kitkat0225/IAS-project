<template>
  <small-card title="Digital Phase Contrast">
    <custom-button icon="play-circle" label="Go" @click="select1" />
    <custom-button icon="cog" label="Set" @click="select2" />
  </small-card>
</template>

<script>
import SmallCard from "../../../custom/SmallCard";
import CustomButton from "../../../custom/CustomButton";

export default {
  name: "DPC",

  components: {
    SmallCard,
    CustomButton
  },

  data: () => ({}),

  methods: {
    select1: function() {
      console.log("Select-1");
    },
    select2: function() {
      console.log("Select-2");
    }
  }
};
</script>
