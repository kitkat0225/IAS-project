<template>
  <tab-item title="View">
    <v-row justify="center">
      <v-container class="max-width pagination">
        <v-pagination
          v-model="curPageIdx"
          class="my-4 pagination"
          total-visible="5"
          :length="allData.length"
          @input="handlePageChange"
        ></v-pagination>
      </v-container>
    </v-row>
    <v-divider></v-divider>
    <Vessel />
    <v-divider></v-divider>
    <Objective />
    <v-divider></v-divider>
    <Channel />
    <v-divider></v-divider>
    <ImageAdjust />
    <!-- <div v-if="seriesCount > 1">
      <v-divider></v-divider>
      <ImageSeries />
    </div> -->
    <div>
      <v-divider></v-divider>
      <ZPosition />
    </div>
    <div>
      <v-divider></v-divider>
      <Timeline />
    </div>
  </tab-item>
</template>

<script>
import { mapGetters, mapState } from "vuex";

import TabItem from "../custom/TabItem";
import Vessel from "./contents/viewcontrol/Vessel";
import Objective from "./contents/viewcontrol/Objective";
import Channel from "./contents/viewcontrol/Channel";
import ImageAdjust from "./contents/viewcontrol/ImageAdjust";
// import ImageSeries from "./contents/viewcontrol/ImageSeries";
import ZPosition from "./contents/viewcontrol/ZPosition";
import Timeline from "./contents/viewcontrol/Timeline";

export default {
  name: "ViewTab",

  components: {
    TabItem,
    Vessel,
    Objective,
    Channel,
    ImageAdjust,
    // ImageSeries,
    ZPosition,
    Timeline
  },

  data: () => ({
    totalPageCnt: 0,
    curPageIdx: 0
  }),

  created() {
    this.curPageIdxWatch = this.$store.watch(
      (state, getters) => getters["image/currentPageIndex"],
      res => {
        this.curPageIdx = res;
      }
    );
  },

  beforeDestroy() {
    this.curPageIdxWatch();
  },

  computed: {
    ...mapGetters("image", {
      seriesCount: "seriesCount",
      selectedImagesAtRowCol: "selectedImagesAtRowCol"
    }),
    ...mapState({
      allData: state => state.image.allData
    }),
    sizeZ: function() {
      let zs = this.selectedImagesAtRowCol.map(img => img.extParams.z);
      zs = [...new Set(zs)];
      return zs.length;
    },
    sizeT: function() {
      let ts = this.selectedImagesAtRowCol.map(img => img.extParams.timeline);
      ts = [...new Set(ts)];
      return ts.length;
    }
  },
  methods: {
    handlePageChange(idx) {
      this.$store.dispatch("image/changeCurrentPage", idx);
    }
  }
};
</script>

<style scoped>
.pagination {
  padding: 0px !important;
}
.pagination >>> button {
  width: 24px;
  height: 24px;
  min-width: 24px;
}
</style>
