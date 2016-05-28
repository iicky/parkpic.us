from pymongo import MongoClient

from parkpic import secrets as sec


class DB:
    ''' Database class
    '''
    def __init__(self):
        ''' Creates database engine
        '''
        self.client = MongoClient(
            'mongodb://%s:%s@%s:27017/parkpic' % (sec.mongouser,
                                                  sec.mongopwd,
                                                  sec.mongohost))
        self.db = self.client.parkpic

        self.parks = self.db.parks
        self.photos = self.db.photos
        self.igphotos = self.db.igphotos
