from collections import Counter
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN

import parkpic as pp


class Clusters:
    ''' Clustering class
    '''
    def __init__(self, parkcode, eps=0.01, min_samples=10):
        self.photos = pp.Park(parkcode).photos()
        self.clusters, self.cluster_count = self.DBSCAN(eps, min_samples)
        self.tags, self.tag_counts = self.autotags()
        self.sim_matrix = self.sim_matrix()
        self.centers = self.centers()

    def DBSCAN(self, eps=0.01, min_samples=10):
        ''' Performs the DBSCAN clustering of photos
        '''
        photos = self.photos
        locations = photos.as_matrix(columns=('longitude', 'latitude'))
        db = DBSCAN(eps=float(eps),
                    min_samples=int(min_samples)).fit(locations)
        labels = db.labels_
        photos['core'] = [True if i in db.core_sample_indices_
                          else False for i in range(0, len(labels))]
        photos['label'] = labels

        return photos, labels.max()+1

    def autotags(self):
        ''' Returns the the autotags and frequencies for each cluster
        '''
        ctags = {}
        ccounts = {}

        for i in range(0, self.clusters.label.max()+1):
            ctags[i] = []
            for tag in self.clusters.autotags[self.clusters.label == i]:
                if tag:
                    ctags[i] = ctags[i] + [t for t in tag
                                           if t != "outdoor" and
                                           t != "indoor"]

            ccounts[i] = Counter(ctags[i])

        return ctags, ccounts

    def jaccard_index(self, a, b):
        ''' Returns the Jaccard Similarity Index between two cluster's tags
        '''
        if len(set(a)) == 0 and len(set(b)) == 0:
            return 0
        else:
            shared = len(set(a).intersection(b))
            return shared / float(len(set(a)) + len(set(b)) - shared)

    def sim_matrix(self):
        ''' Returns a numpy matrix of Jaccard Similarities between clusters
        '''
        jacindex = np.zeros(shape=(len(self.tags), len(self.tags)))

        for a in self.tags:
            for b in self.tags:
                    if not a == b:
                        ji = round(self.jaccard_index(self.tags[a],
                                                      self.tags[b]), 2)
                        jacindex[a][b] = ji
                    else:
                        jacindex[a][b] = "-1"
        return jacindex

    def sim_clusters(self, label):
        ''' Returns a tupled array of similar clusters by label
        '''
        similar = []
        simC = sorted(range(len(self.sim_matrix[label])),
                      key=lambda z: self.sim_matrix[label][z],
                      reverse=True)[:5]
        for s in simC:
            if s == label and len(simC) == 1:
                similar = None
            if not s == label:
                similar.append((str(s+1),
                               int(self.sim_matrix[label][s]*100)))
        return similar

    def centers(self):
        ''' Returns a dataframe of cluster summary information
        '''
        clusters = self.clusters
        clusters['group'] = clusters.label
        columns = ['latitude', 'longitude', 'label', 'group']
        centers = clusters[columns].groupby('group').mean()
        centers['label'] = centers.label.astype(int)
        return centers

    def ind_markers(self):
        ''' Returns a dictionary of individual marker information
        '''
        cl = self.clusters
        cl['cluster'] = cl.label.apply(lambda x: 'Noise' if x < 0
                                       else x + 1)
        cl['marker'] = cl.label.apply(lambda x:
                                      'static/icons/ind/X.png' if x < 0 else
                                      'static/icons/ind/%s.png' % str(x + 1))

        return cl.to_dict(orient="records")

    def cen_markers(self):
        ''' Returns a dictionary of cluster center marker information
        '''
        cl = self.centers[self.centers.label >= 0].copy()

        cl['cluster'] = cl.label.apply(lambda x: x + 1)
        cl['marker'] = cl.label.apply(lambda x: ('static/icons/cen/%s.png'
                                                 % str(x + 1)))
        # Top 5 most common cluster tags
        cl['toptags'] = cl.label.apply(lambda x:
                                       self.tag_counts[x].most_common(5))
        # Similar clusters and scores
        cl['similar'] = cl.label.apply(lambda x: self.sim_clusters(x))

        # Number of photos and users
        cl['nophotos'] = cl.label.apply(lambda x:
                                        len(self.photos
                                            [self.photos.label == x]))
        cl['nousers'] = cl.label.apply(lambda x:
                                       self.photos[self.photos.label == x]
                                       .username.nunique())

        return cl.to_dict(orient="records")

    def carousel(self):
        ''' Returns a dictionary of carousel photos
        '''
        df = self.photos
        df = df[df.label >= 0].copy()

        cols = ['username', 'square_link', 'taken', 'photopage', 'label']
        df = df[cols]

        return {k: v.sort_values(by='taken', ascending=False)
                    .to_dict(orient='records')
                for k, v in df.groupby('label')}


class IGClusters:
    ''' Instagram Clustering class
    '''
    def __init__(self, parkcode, eps, min_samples):
        self.photos = pp.Park(parkcode).igphotos()
        self.clusters, self.cluster_count = self.DBSCAN(eps, min_samples)
        self.centers = self.centers()

    def DBSCAN(self, eps, min_samples):
        ''' Performs the DBSCAN clustering of photos
        '''
        photos = self.photos
        locations = photos.as_matrix(columns=('longitude', 'latitude'))
        db = DBSCAN(eps=float(eps),
                    min_samples=int(min_samples)).fit(locations)
        labels = db.labels_
        photos['core'] = [True if i in db.core_sample_indices_
                          else False for i in range(0, len(labels))]
        photos['label'] = labels

        return photos, labels.max()+1

    def centers(self):
        ''' Returns a dataframe of cluster summary information
        '''
        clusters = self.clusters
        clusters['group'] = clusters.label
        columns = ['latitude', 'longitude', 'label', 'group']
        centers = clusters[columns].groupby('group').mean()
        centers['label'] = centers.label.astype(int)
        return centers

    def cen_markers(self):
        ''' Returns a dictionary of cluster center marker information
        '''
        cl = self.centers[self.centers.label >= 0].copy()

        cl['cluster'] = cl.label.apply(lambda x: x + 1)
        cl['marker'] = cl.label.apply(lambda x: ('static/icons/cen/%s.png'
                                                 % str(x + 1)))
        # Number of photos and users
        cl['nophotos'] = cl.label.apply(lambda x:
                                        len(self.photos
                                            [self.photos.label == x]))
        return cl.to_dict(orient="records")

    def ind_markers(self):
        ''' Returns a dictionary of individual marker information
        '''
        cl = self.photos
        cl['cluster'] = cl.label.apply(lambda x: 'Noise' if x < 0
                                       else x + 1)
        cl['marker'] = cl.label.apply(lambda x:
                                      'static/icons/ind/X.png' if x < 0 else
                                      'static/icons/ind/%s.png' % str(x + 1))

        return cl.to_dict(orient="records")
