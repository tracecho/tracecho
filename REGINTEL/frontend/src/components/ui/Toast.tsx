import toastBase, { Toaster as HotToaster, ToastOptions } from "react-hot-toast";

const defaultStyle = {
  borderRadius: "8px",
  background: "#FFFFFF",
  color: "#202C2A",
  border: "1px solid #E2E9E6",
  boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
  fontSize: "14px",
  padding: "10px 16px",
};

export const toast = {
  ...toastBase,
  success: (message: string, options?: ToastOptions) =>
    toastBase.success(message, {
      style: {
        ...defaultStyle,
        borderColor: "#167568",
      },
      iconTheme: {
        primary: "#167568",
        secondary: "#FFFFFF",
      },
      ...options,
    }),
  error: (message: string, options?: ToastOptions) =>
    toastBase.error(message, {
      style: {
        ...defaultStyle,
        borderColor: "#DC2626",
      },
      iconTheme: {
        primary: "#DC2626",
        secondary: "#FFFFFF",
      },
      ...options,
    }),
  info: (message: string, options?: ToastOptions) =>
    toastBase(message, {
      style: defaultStyle,
      ...options,
    }),
};

export const Toaster = () => {
  return (
    <HotToaster
      position="top-right"
      toastOptions={{
        duration: 4000,
        style: defaultStyle,
        success: {
          iconTheme: {
            primary: "#167568",
            secondary: "#FFFFFF",
          },
        },
        error: {
          iconTheme: {
            primary: "#DC2626",
            secondary: "#FFFFFF",
          },
        },
      }}
    />
  );
};

export default toast;
