import aq

class PlanRecord(aq.Record):

    def __init__(self,model,data):
        self.name = "Untitled Plan"
        self.id = None
        self.status = "planning"
        super(PlanRecord,self).__init__(model,data)
        self.has_many_generic("data_associations", aq.DataAssociation)
        self.has_many(
            "operations", aq.Operation,
            {"through": aq.PlanAssociation, "association": "operation"})
        self.has_many("wires", aq.Wire, opts={"no_getter": True})

    def add_operation(self,operation):
        self.append_association("operations", operation)
        return self

    def wire(self,source, destination):
        wire = aq.Wire.record({})
        wire.set_association("source", source) \
            .set_association("destination", destination)
        self.append_association("wires", wire)
        return self

    def submit(self, user, budget):
        user_query = "&user_id=" + str(user.id)
        budget_query = "?budget_id=" + str(budget.id)
        r = aq.http.get('/plans/start/'+str(self.id)+budget_query+user_query)
        print(r)

    def show(self):
        print(self.name + " id: " + str(self.id))
        for operation in self.operations:
            operation.show(pre="  ")
        for wire in self.wires:
            wire.show(pre="  ")

    def save(self):
        if not self.id:
            user_query = "?user_id=" + str(aq.User.current.id)
            r = aq.http.post('/plans.json'+user_query,self.to_json())
            if "errors" in r:
                raise Exception("Could not save plan: " + str(r["errors"]))
            new_plan = aq.Plan.record(r)
            self.id = new_plan.id
            self.operations = new_plan.operations
            self.wires = new_plan.wires
        else:
            print("WARNING: Plan " + self.id +
                  " already saved. Cannot save again.")
        return self

    def estimate_cost(self):
        r = aq.http.post('/launcher/estimate',{ "id": self.id} )
        for op in self.operations:
            for c in r["costs"]:
                if c["id"] == op.id:
                    op.cost = c

    def to_json(self):
        return {
            "name": self.name,
            "operations": [ op.to_json() for op in self.operations ],
            "wires": [ wire.to_json() for wire in self.wires ],
            "rid": self.rid,
            "layout": {"id": 0, "parent_id": -1, "wires": [], "name": "no name"},
            "status": self.status
        }

class PlanModel(aq.Base):

    def __init__(self):
        super(PlanModel,self).__init__("Plan")

    def find(self,id):
        """Override find for plans, because the generic method is too minimal"""
        return aq.Plan.record(aq.http.get("/plans/" + str(id) + ".json"))

Plan = PlanModel()
