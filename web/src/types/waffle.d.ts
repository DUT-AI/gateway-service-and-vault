declare global {
  namespace JSX {
    interface IntrinsicElements {
      "dutai-waffle": React.DetailedHTMLProps<
        React.HTMLAttributes<HTMLElement> & {
          current?: string;
        },
        HTMLElement
      >;
    }
  }
}

declare module "react" {
  namespace JSX {
    interface IntrinsicElements {
      "dutai-waffle": React.DetailedHTMLProps<
        React.HTMLAttributes<HTMLElement> & {
          current?: string;
        },
        HTMLElement
      >;
    }
  }
}

export {};
