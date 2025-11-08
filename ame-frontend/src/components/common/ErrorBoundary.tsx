import { Component, ErrorInfo, ReactNode } from 'react';
import { Result, Button } from 'antd';

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * 错误边界组件
 * 捕获子组件树中的 JavaScript 错误，记录错误并展示降级 UI
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(_error: Error): Partial<ErrorBoundaryState> {
    // 更新 state 使下一次渲染能够显示降级后的 UI
    return { hasError: true };
  }

  componentDidCatch(_error: Error, errorInfo: ErrorInfo): void {
    // 将错误记录到错误报告服务
    console.error('ErrorBoundary caught an error:', _error, errorInfo);
    this.setState({
      error: _error,
      errorInfo,
    });
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  handleReload = (): void => {
    window.location.reload();
  };

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '50px', textAlign: 'center' }}>
          <Result
            status="error"
            title="页面渲染出错"
            subTitle={
              <div>
                <p>{this.state.error?.message || '发生了未知错误'}</p>
                {this.state.errorInfo && (
                  <details style={{ whiteSpace: 'pre-wrap', textAlign: 'left', marginTop: '20px' }}>
                    <summary>错误详情 (开发模式)</summary>
                    <p style={{ marginTop: '10px' }}>
                      {this.state.error && this.state.error.toString()}
                    </p>
                    <p>{this.state.errorInfo.componentStack}</p>
                  </details>
                )}
              </div>
            }
            extra={[
              <Button type="primary" key="reload" onClick={this.handleReload}>
                刷新页面
              </Button>,
              <Button key="reset" onClick={this.handleReset}>
                返回上一步
              </Button>,
            ]}
          />
        </div>
      );
    }

    return this.props.children;
  }
}
