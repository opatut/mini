from datetime import datetime

class Commit(object):
    def __init__(self, network, raw):
        self.network = network
        self.raw = raw
        self.number = -1
        self.lane = None
        self.date = datetime.fromtimestamp(raw.committed_date + raw.committer_tz_offset)
        self.children = []
        self.parents = []
        self.branches = []
        self.tags = []

    def get_child_lane_endings(self):
        lanes = []
        for lane in self.network.lanes:
            if lane.commits[-1] in self.children:
                lanes.append(lane)
        return lanes

    def find_last_child(self):
        last = None
        for child in self.children:
            if not last or child.number > last.number:
                last = child
        return last

class Lane(object):
    def __init__(self, network, number):
        self.network = network
        self.number = number
        self.commits = []
        self.start = None
        self.end = None

    def insert(self, commit):
        self.commits.append(commit)
        commit.lane = self

    def check_closed(self):
        closed = True
        commit = self.commits[-1]
        # this lane can be closed if all parents have a lane
        for parent in commit.parents:
            if not parent.lane:
                closed = False
        if closed:
            self.end = max([parent.number for parent in commit.parents]) if commit.parents else commit.number

class Network(object):
    def __init__(self, repository):
        self.repository = repository
        self.lanes = []
        self.commit_number = 0
        self.commits = []

    def generate(self):
        self.fetch_commits()

        for commit in self.commits:
            ending_lanes = commit.get_child_lane_endings()
            if ending_lanes:
                ending_lanes.sort(key=lambda x: x.number)
                lane = ending_lanes[0]
                lane.insert(commit)
                for lane in ending_lanes:
                    lane.check_closed()
            else:
                child = commit.find_last_child()
                if child and child.lane:
                    new_lane_number = child.lane.number + 1
                    lane_number = new_lane_number 
                    # push down lanes
                    lanes_to_push = 0
                    while True:
                        if not self.get_lane_at(commit.number, lane_number):
                            break
                        lanes_to_push += 1
                        lane_number += 1
                    for i in range(lanes_to_push):
                        print(new_lane_number, lanes_to_push, i)
                        self.get_lane_at(commit.number, new_lane_number + lanes_to_push - i - 1).number += 1
                else:
                    new_lane_number = 0
                    while True:
                        if not self.get_lane_at(commit.number, new_lane_number):
                            break
                        new_lane_number += 1

                new_lane = Lane(self, new_lane_number)
                new_lane.start = min([child.number for child in commit.children]) if commit.children else commit.number
                new_lane.insert(commit)
                new_lane.check_closed()
                self.lanes.append(new_lane)

    def get_lane_at(self, commit_number, lane_number):
        for lane in self.lanes:
            if lane.number != lane_number: continue
            if lane.end is None or lane.end >= commit_number:
                return lane
        return None

    def fetch_commits(self):
        # create commit objects and sort by date
        self.commits = [Commit(self, c) for c in self.repository.get_commits()]
        self.commits.sort(key=lambda x: x.date, reverse=True)

        # create hash lookup table
        self.commit_lookup = {c.raw.hexsha: c for c in self.commits}

        # set commit numbers
        for index, commit in enumerate(self.commits):
            commit.number = index

        # fill parent/child links
        for commit in self.commits:
            for parent_hash in commit.raw.parents:
                parent = self.commit_lookup[parent_hash.hexsha]
                commit.parents.append(parent) 
                parent.children.append(commit)

        # fill commit tags/branches
        for commit in self.commits:
            for branch in self.repository.git.branches:
                if branch.commit.hexsha == commit.raw.hexsha:
                    commit.branches.append(branch)
            for tag in self.repository.git.tags:
                if tag.commit.hexsha == commit.raw.hexsha:
                    commit.tags.append(tag)

        # normalize commit numbers
        commits = list(self.commits)
        for commit in commits:
            for child in commit.children:
                # damn, we are behind our child
                if commit.number < child.number:
                    child_number = child.number
                    # move child and everything in between one forward
                    for i in range(commit.number+1, child.number+1):
                        self.commits[i].number -= 1
                    commit.number = child_number

                    # sort again to make numbers indices
                    self.commits.sort(key=lambda x: x.number)

