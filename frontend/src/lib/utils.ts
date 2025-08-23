import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: Date | string, format: 'full' | 'short' = 'full'): string {
  const d = new Date(date);
  
  if (format === 'short') {
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }
  
  return d.toLocaleDateString('en-US', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });
}

export function formatMinutes(minutes: number): string {
  if (minutes < 60) {
    return `${minutes}m`;
  }
  
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  
  if (remainingMinutes === 0) {
    return `${hours}h`;
  }
  
  return `${hours}h ${remainingMinutes}m`;
}

export function formatDuration(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  
  return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
}

export function formatCurrency(amount: number): string {
  return amount.toLocaleString();
}

export function getMoodEmoji(mood: number): string {
  if (mood >= 9) return '🥳';
  if (mood >= 7) return '😄';
  if (mood >= 5) return '🙂';
  if (mood >= 3) return '😐';
  if (mood >= 1) return '😔';
  return '😢';
}

export function getMoodColor(mood: number): string {
  if (mood >= 8) return 'text-green-600';
  if (mood >= 6) return 'text-blue-600';
  if (mood >= 4) return 'text-yellow-600';
  if (mood >= 2) return 'text-orange-600';
  return 'text-red-600';
}

export function getTaskPriorityColor(priority: string): string {
  switch (priority) {
    case 'URGENT': return 'text-red-600';
    case 'HIGH': return 'text-orange-600';
    case 'MEDIUM': return 'text-blue-600';
    case 'LOW': return 'text-green-600';
    default: return 'text-gray-600';
  }
}

export function getDifficultyStars(difficulty: number): number {
  return Math.round(difficulty);
}

export function getFileExtension(filename: string): string {
  return filename.split('.').pop()?.toLowerCase() || '';
}

export function isImageFile(filename: string): boolean {
  const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'];
  return imageExtensions.includes(getFileExtension(filename));
}
