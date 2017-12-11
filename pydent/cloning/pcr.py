import aq

class Plan(aq.PlanRecord):

    def __init__(self,name):

        super(Plan,self).__init__(aq.Plan,{"name": name})

        # Define operations. The x and y positions are optional, but improve layout in the GUI
        self.pcr = aq.OperationType.find_by_name("Make PCR Fragment").instance(x_pos=32,y_pos=240)
        self.pour = aq.OperationType.find_by_name("Pour Gel").instance(x_pos=240,y_pos=240)
        self.run = aq.OperationType.find_by_name("Run Gel").instance(x_pos=140,y_pos=160)
        self.extract = aq.OperationType.find_by_name("Extract Gel Slice").instance(x_pos=144,y_pos=96)
        self.purify = aq.OperationType.find_by_name("Purify Gel Slice").instance(x_pos=144,y_pos=32)

        # Add operations to the plan
        self.add_operations([self.pcr, self.pour, self.run, self.extract, self.purify])

        # Connect wires
        self.add_wires([
            [self.pcr.output("Fragment"),self.run.input("Fragment")],
            [self.pour.output("Lane"),self.run.input("Gel")],
            [self.run.output("Fragment"),self.extract.input("Fragment")],
            [self.extract.output("Fragment"),self.purify.input("Gel")]
        ])

    def set_output(self,sample,container):
        self.set(self.pcr.output("Fragment"),sample,container)
        return self