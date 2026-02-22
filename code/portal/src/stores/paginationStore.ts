import { defineStore } from "pinia"
import { reactive } from "vue"

export const usePaginationStore = defineStore("pagination", () => {
  const pagination = reactive({
    page: 1,
    limit: 5,
    total: 0
  })

  function setPage(page: number) {
    pagination.page = page
  }

  function setLimit(limit: number) {
    pagination.limit = limit
    pagination.page = 1
  }

  function setTotal(total: number) {
    pagination.total = total
  }

  function resetPagination() {
    pagination.page = 1
    pagination.total = 0
  }

  return {
    pagination,
    setPage,
    setLimit,
    setTotal,
    resetPagination
  }
})
