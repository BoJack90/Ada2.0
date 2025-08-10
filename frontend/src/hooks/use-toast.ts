import toast from 'react-hot-toast'

export const useToast = () => {
  const showToast = {
    success: (message: string) => {
      toast.success(message)
    },
    error: (message: string) => {
      toast.error(message)
    },
    info: (message: string) => {
      toast(message, {
        icon: 'ℹ️',
      })
    },
    loading: (message: string) => {
      return toast.loading(message)
    },
    promise: <T,>(
      promise: Promise<T>,
      messages: {
        loading: string
        success: string | ((data: T) => string)
        error: string | ((err: any) => string)
      }
    ) => {
      return toast.promise(promise, messages)
    },
    dismiss: (toastId?: string) => {
      toast.dismiss(toastId)
    },
  }

  return showToast
}

// Export dla łatwiejszego importu
export { toast }