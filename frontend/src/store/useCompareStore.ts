import { create } from 'zustand';
import toast from 'react-hot-toast';

interface CompareState {
  compareIds: number[];
  addId: (id: number) => void;
  removeId: (id: number) => void;
  clearAll: () => void;
}

export const useCompareStore = create<CompareState>((set, get) => ({
  compareIds: [],
  
  addId: (id) => {
    const currentIds = get().compareIds;
    
    if (currentIds.includes(id)) {
      toast('Este producto ya está en el ring', { icon: 'ℹ️' });
      return;
    }
    
    if (currentIds.length >= 4) {
      toast.error('Límite de 4 productos alcanzado. Si quieres añadir otro, debes eliminar uno de ellos.', {
        style: { maxWidth: '500px' }
      });
      return;
    }
    
    set({ compareIds: [...currentIds, id] });
    toast.success('Producto añadido a la comparativa');
  },
  
  removeId: (id) => {
    set((state) => ({
      compareIds: state.compareIds.filter((currentId) => currentId !== id)
    }));
  },
  
  clearAll: () => set({ compareIds: [] }),
}));
