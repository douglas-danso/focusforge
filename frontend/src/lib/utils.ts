import { type ClassValue, clsx } from "clsx"
// import { twMerge } from "tailwind-merge"

// Enhanced cn function that handles common Tailwind class conflicts without twmerge
export function cn(...inputs: ClassValue[]) {
  const classes = clsx(inputs);
  
  // Simple conflict resolution for common cases
  return classes
    // Handle spacing conflicts (p, px, py, pt, pb, pl, pr)
    .replace(/\b(p|px|py|pt|pb|pl|pr)-\d+/g, (match) => {
      // Keep the last occurrence of spacing classes
      const parts = classes.split(' ').filter(c => c.match(/\b(p|px|py|pt|pb|pl|pr)-\d+/));
      return parts[parts.length - 1] || match;
    })
    // Handle margin conflicts (m, mx, my, mt, mb, ml, mr)
    .replace(/\b(m|mx|my|mt|mb|ml|mr)-\d+/g, (match) => {
      const parts = classes.split(' ').filter(c => c.match(/\b(m|mx|my|mt|mb|ml|mr)-\d+/));
      return parts[parts.length - 1] || match;
    })
    // Handle width conflicts
    .replace(/\bw-\d+/g, (match) => {
      const parts = classes.split(' ').filter(c => c.match(/\bw-\d+/));
      return parts[parts.length - 1] || match;
    })
    // Handle height conflicts
    .replace(/\bh-\d+/g, (match) => {
      const parts = classes.split(' ').filter(c => c.match(/\bh-\d+/));
      return parts[parts.length - 1] || match;
    })
    // Handle text size conflicts
    .replace(/\btext-\w+/g, (match) => {
      const parts = classes.split(' ').filter(c => c.match(/\btext-\w+/));
      return parts[parts.length - 1] || match;
    })
    // Handle background color conflicts
    .replace(/\bbg-\w+/g, (match) => {
      const parts = classes.split(' ').filter(c => c.match(/\bbg-\w+/));
      return parts[parts.length - 1] || match;
    })
    // Handle text color conflicts
    .replace(/\btext-\w+/g, (match) => {
      const parts = classes.split(' ').filter(c => c.match(/\btext-\w+/));
      return parts[parts.length - 1] || match;
    })
    // Handle border color conflicts
    .replace(/\bborder-\w+/g, (match) => {
      const parts = classes.split(' ').filter(c => c.match(/\bborder-\w+/));
      return parts[parts.length - 1] || match;
    })
    // Handle flex direction conflicts
    .replace(/\bflex-\w+/g, (match) => {
      const parts = classes.split(' ').filter(c => c.match(/\bflex-\w+/));
      return parts[parts.length - 1] || match;
    })
    // Handle justify content conflicts
    .replace(/\bjustify-\w+/g, (match) => {
      const parts = classes.split(' ').filter(c => c.match(/\bjustify-\w+/));
      return parts[parts.length - 1] || match;
    })
    // Handle align items conflicts
    .replace(/\bitems-\w+/g, (match) => {
      const parts = classes.split(' ').filter(c => c.match(/\bitems-\w+/));
      return parts[parts.length - 1] || match;
    })
    // Handle position conflicts
    .replace(/\b(relative|absolute|fixed|sticky)/g, (match) => {
      const parts = classes.split(' ').filter(c => c.match(/\b(relative|absolute|fixed|sticky)/));
      return parts[parts.length - 1] || match;
    })
    // Handle display conflicts
    .replace(/\b(block|inline|inline-block|flex|grid|hidden)/g, (match) => {
      const parts = classes.split(' ').filter(c => c.match(/\b(block|inline|inline-block|flex|grid|hidden)/));
      return parts[parts.length - 1] || match;
    });
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
