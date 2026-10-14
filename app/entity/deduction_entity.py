class DeductionEntity:
    def __init__(this):
        this.code = ""
        this.name = ""
        this.floor = 0.0
        this.ceil = 0.0
        this.value = 0.0
        this.view_only = 0.0
        this.active = "" # y or n
        this.type = "" # c or r
        this.payroll_design = ""
        this.bracket = None
        this.datecreated = ""
        this.createdby = ""

# this is the bracket entity
class BraketEntity:
    def __init__t(this):
        #{"bracket": 1, "from": 0, "to": 250000, "fix_tax": 0, "rate_on_excess": 0},
        this.braket: int = None
        this.frm: float  = 0.0 # this is fr
        this.to: float = 0.0
        this.fix_tax: float = 0.0
        this.rate_on_excess = 0.0 # this is a percentage


class PayrollEntity:
    def __init__(this):
        this.refid = ""
        this.from_ = ""
        this.to = ""
        this.cutoff = ""
        this.type = ""
        this.datecreated = ""
        this.createdby = ""
        this.deduction_list = []
        this.signatory_list = []
