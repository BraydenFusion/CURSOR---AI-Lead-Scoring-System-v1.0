import React, { Component, ReactNode } from "react";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.href = "/dashboard";
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="text-red-600">Something went wrong</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-gray-600">
                We encountered an unexpected error. Please try refreshing the page.
              </p>
              {process.env.NODE_ENV === "development" && this.state.error && (
                <div className="bg-gray-100 p-3 rounded text-xs font-mono overflow-auto">
                  <p className="font-semibold mb-2">Error details:</p>
                  <pre className="whitespace-pre-wrap">{this.state.error.message}</pre>
                  {this.state.error.stack && (
                    <details className="mt-2">
                      <summary className="cursor-pointer text-blue-600">Stack trace</summary>
                      <pre className="mt-2 whitespace-pre-wrap text-xs">{this.state.error.stack}</pre>
                    </details>
                  )}
                </div>
              )}
              <div className="flex gap-2">
                <Button onClick={this.handleReset} className="flex-1">
                  Go to Dashboard
                </Button>
                <Button onClick={() => window.location.reload()} variant="outline" className="flex-1">
                  Refresh Page
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

