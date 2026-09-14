import { Toaster as Sonner } from "sonner";

type ToasterProps = React.ComponentProps<typeof Sonner>;

function Toaster({ ...props }: ToasterProps) {
  return (
    <Sonner
      theme="light"
      position="bottom-right"
      toastOptions={{
        classNames: {
          toast:
            "group toast bg-canvas text-ink border border-line shadow-elevated rounded-lg font-sans",
          description: "text-ink-secondary",
          actionButton: "bg-primary text-primary-foreground",
          cancelButton: "bg-surface-subtle text-ink-secondary",
        },
      }}
      {...props}
    />
  );
}

export { Toaster };
