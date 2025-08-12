import { useRef, useCallback, useEffect } from 'react';

export const useDragScroll = () => {
  const scrollRef = useRef<HTMLElement>(null);
  const isDown = useRef(false);
  const startX = useRef(0);
  const scrollLeft = useRef(0);
  const hasDragged = useRef(false);

  const handleMouseDown = useCallback((e: MouseEvent) => {
    if (!scrollRef.current) return;
    
    console.log('Drag start:', {
      element: scrollRef.current,
      scrollLeft: scrollRef.current.scrollLeft,
      scrollWidth: scrollRef.current.scrollWidth,
      clientWidth: scrollRef.current.clientWidth
    });
    
    isDown.current = true;
    hasDragged.current = false;
    
    scrollRef.current.style.cursor = 'grabbing';
    
    startX.current = e.pageX - scrollRef.current.offsetLeft;
    scrollLeft.current = scrollRef.current.scrollLeft;
  }, []);

  const handleMouseLeave = useCallback(() => {
    isDown.current = false;
    if (scrollRef.current) {
      scrollRef.current.style.cursor = 'grab';
    }
  }, []);

  const handleMouseUp = useCallback(() => {
    isDown.current = false;
    if (scrollRef.current) {
      scrollRef.current.style.cursor = 'grab';
    }
  }, []);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isDown.current || !scrollRef.current) return;
    
    e.preventDefault();
    hasDragged.current = true;
    
    const x = e.pageX - scrollRef.current.offsetLeft;
    const walkX = (x - startX.current) * 1; // Scroll speed multiplier
    
    // Only handle horizontal scrolling
    const newScrollLeft = scrollLeft.current - walkX;
    scrollRef.current.scrollLeft = newScrollLeft;
    
    console.log('Drag move:', {
      walkX,
      newScrollLeft,
      actualScrollLeft: scrollRef.current.scrollLeft
    });
  }, []);

  // Prevent click events on cells when dragging has occurred
  const handleClick = useCallback((e: Event) => {
    if (hasDragged.current) {
      e.preventDefault();
      e.stopPropagation();
      hasDragged.current = false;
    }
  }, []);

  useEffect(() => {
    const element = scrollRef.current;
    if (!element) return;

    element.addEventListener('mousedown', handleMouseDown);
    element.addEventListener('mouseleave', handleMouseLeave);
    element.addEventListener('mouseup', handleMouseUp);
    element.addEventListener('mousemove', handleMouseMove);
    element.addEventListener('click', handleClick, true); // Use capture phase

    return () => {
      element.removeEventListener('mousedown', handleMouseDown);
      element.removeEventListener('mouseleave', handleMouseLeave);
      element.removeEventListener('mouseup', handleMouseUp);
      element.removeEventListener('mousemove', handleMouseMove);
      element.removeEventListener('click', handleClick, true);
    };
  }, [handleMouseDown, handleMouseLeave, handleMouseUp, handleMouseMove, handleClick]);

  return scrollRef;
};