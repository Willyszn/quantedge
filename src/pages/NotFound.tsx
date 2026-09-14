import { Link } from "react-router-dom";
import { Compass } from "lucide-react";
import { Button } from "@/components/ui/button";

export function NotFound() {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-3 px-4 py-24 text-center">
      <Compass className="h-8 w-8 text-ink-faint" />
      <h1 className="text-xl font-semibold text-ink">Page not found</h1>
      <p className="max-w-sm text-sm text-ink-secondary">
        The page you're looking for doesn't exist or has moved.
      </p>
      <Button asChild className="mt-2">
        <Link to="/">Back to Dashboard</Link>
      </Button>
    </div>
  );
}
