import pandas as pd
import shapely.geometry

import parkpic as pp


class Parks:
    ''' Retreive park information
    '''
    def __init__(self):
        pass

    def in_db(self, parkname):
        ''' Returns True if parkname in database
        '''
        result = pp.db.parks.find_one({'parkname': parkname})
        if result:
            return True
        return False

    def parkname_to_code(self, parkname):
        ''' Returns a parkcode from parkname
        '''
        result = pp.db.parks.find_one(
                    {'parkname': parkname},
                    {'parkcode': 1}
                )
        if result:
            return result['parkcode']
        return None


class Park:
    '''  Park object
    '''
    def __init__(self, parkcode):
        result = pp.db.parks.find_one({'parkcode': parkcode})
        self.parkname = result['parkname']
        self.parkcode = result['parkcode']
        self.area = result['area']
        self.latitude = result['latitude']
        self.longitude = result['longitude']
        self.type = result['type']
        self.boundary = result['boundary']
        self.photo_count = self.photos()._id.count()
        # self.igphoto_count = self.igphotos()._id.count()

    def in_park(self, lat, lon):
        ''' Returns true if point is within park boundaries
        '''
        shape = shapely.geometry.asShape(self.boundary)
        point = shapely.geometry.Point(lon, lat)
        return shape.contains(point)

    def random_point(self):
        ''' Returns a random point within a park
        '''
        shape = shapely.geometry.asShape(self.boundary)
        xmax, ymax, xmin, ymin = shape.bounds

        random_point = shapely.geometry.Point(
                        xmin + (random.random() * (xmax-xmin)),
                        ymin + (random.random() * (ymax-ymin)))
        while not shape.contains(random_point):
            random_point = shapely.geometry.Point(
                xmin + (random.random() * (xmax-xmin)),
                ymin + (random.random() * (ymax-ymin)))

        return {'lon': random_point.x, 'lat': random_point.y}

    def map_boundary(self):
        ''' Returns Google Maps formatted park boundary
        '''
        geom = self.boundary['coordinates']
        mapco = []
        for i in range(0, len(geom)):
            try:
                coords = [{'lat': c[1], 'lng': c[0]}
                          for coord in geom[i] for c in coord]
            except:
                coords = [{'lat': c[1], 'lng': c[0]}
                          for c in geom[i]]
            mapco.append(coords)
        return mapco

    def photos(self):
        ''' Returns a pandas dataframe of park photos
        '''
        photos = list(pp.db.photos.find(
            {'parkname': self.parkname,
             'in_park': True,
             'canblog': True
             }))

        df = pd.DataFrame(photos)

        return df

    def igphotos(self):
        ''' Returns a pandas dataframe of park photos
        '''
        photos = list(pp.db.igphotos.find(
            {'parkcode': self.parkcode,
             'in_park': True
             }))

        df = pd.DataFrame(photos)
        df['latitude'] = df.location.apply(lambda x: x['latitude'])
        df['longitude'] = df.location.apply(lambda x: x['longitude'])

        return df
