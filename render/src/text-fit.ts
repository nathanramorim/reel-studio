/** Estimativa simples de tamanho de fonte para caber na largura (sem medir DOM). */
export const fitFontSize = (text: string, maxWidth: number, maxSize: number, minSize = 32): number => {
  const estWidth = (size: number) => text.length * size * 0.56;
  let size = maxSize;
  while (size > minSize && estWidth(size) > maxWidth) size -= 2;
  return size;
};
