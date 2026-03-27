import { useState } from 'react';
import { Star } from 'lucide-react';

export default function StarRating({ rating = 0, onRate, size = 20, interactive = true }) {
  const [hover, setHover] = useState(0);

  return (
    <div className="star-rating" style={{ display: 'flex', gap: '2px' }}>
      {[1, 2, 3, 4, 5].map((starIdx) => {
        const active = starIdx <= (hover || rating);
        return (
          <span
            key={starIdx}
            className={`star ${active ? 'active' : ''} ${starIdx <= hover ? 'hover' : ''}`}
            style={{ cursor: interactive ? 'pointer' : 'default', color: active ? 'var(--warning)' : 'var(--outline)' }}
            onClick={() => interactive && onRate && onRate(starIdx)}
            onMouseEnter={() => interactive && setHover(starIdx)}
            onMouseLeave={() => interactive && setHover(0)}
          >
            <Star 
              size={size} 
              fill={active ? 'currentColor' : 'none'} 
              strokeWidth={active ? 0 : 2} 
            />
          </span>
        );
      })}
    </div>
  );
}
