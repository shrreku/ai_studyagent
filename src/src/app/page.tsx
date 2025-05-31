import Image from "next/image";

import InputForm from '@/components/forms/input-form';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 bg-gray-50">
      <div className="w-full max-w-2xl">
        <header className="mb-10 text-center">
          <h1 className="text-4xl font-bold text-gray-800">IntelliStudy Agent</h1>
          <p className="mt-2 text-lg text-gray-600">Tell us about your study needs, and we'll generate a personalized plan for you.</p>
        </header>
        <InputForm />
      </div>
    </main>
  );
}
