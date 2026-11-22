import { RegisterForm } from "@/features/auth";

export default function RegisterPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gray-50 p-4">
      <div className="w-full max-w-sm rounded-lg border border-gray-200 bg-white p-6 shadow-md">
        <h1 className="mb-6 text-center text-2xl font-bold text-gray-900">
          Đăng ký tài khoản
        </h1>
        <RegisterForm />
      </div>
    </main>
  );
}
