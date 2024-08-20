from math import ceil
class Paginator:
    def __init__(self, array: list|tuple , page:int = 1, per_page:int = 1):
        self.array = array
        self.page = page
        self.per_page = per_page
        self.long = len(array)
        self.pages = ceil(self.long/ self.per_page)

    def __get_slice(self):
        start = (self.page - 1) * self.per_page
        stop = start + self.per_page
        return self.array[start:stop]
    
    def get_page(self):
        page_items = self.__get_slice()
        return page_items
    
    def has_next(self):
        if self.page<self.pages:
            return self.page+1
        return False
    
    def has_previous(self):
        if self.page >1:
            return self.page -1
        return False
    
    def get_next(self):
        result = self.has_next()
        if result:
            self.page = result
            return self.get_page()
        raise IndexError(f'Next page does not exist. Use has_next() to check before.')
    
    def get_previous(self):
        result = self.has_previous()
        if result:
            self.page = result
            return self.__get_slice()
        raise IndexError(f'Previous page does not exist. Use has_previous() to check before.')
