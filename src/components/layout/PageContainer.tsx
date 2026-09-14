import { cn } from "@/lib/utils";

interface PageContainerProps {
  title?: string;
  subtitle?: string;
  actions?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

export function PageContainer({ title, subtitle, actions, children, className }: PageContainerProps) {
  return (
    <div className="mx-auto w-full max-w-[1400px] px-4 pb-24 pt-6 sm:px-6 md:pb-10 lg:px-8">
      {(title || actions) && (
        <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            {title && <h1 className="text-2xl font-bold tracking-tight text-ink sm:text-[28px]">{title}</h1>}
            {subtitle && <p className="mt-1 text-sm text-ink-secondary">{subtitle}</p>}
          </div>
          {actions && <div className="flex shrink-0 items-center gap-2">{actions}</div>}
        </div>
      )}
      <div className={cn(className)}>{children}</div>
    </div>
  );
}
