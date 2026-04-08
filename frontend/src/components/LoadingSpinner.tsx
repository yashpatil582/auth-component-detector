export default function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center py-12 gap-3">
      <div className="w-10 h-10 border-4 border-gray-200 border-t-emerald-500 rounded-full animate-spin" />
      <p className="text-sm text-gray-500">Scraping and analyzing page...</p>
    </div>
  );
}
