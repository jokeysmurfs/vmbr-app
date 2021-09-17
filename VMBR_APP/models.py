# coding=UTF-8

from VMBR_APP import db

class VMInf(db.Model):    
    VM_id = db.Column(db.Integer, primary_key=True) 
    VM_uuids = db.Column(db.String(120))
    VM_os = db.Column(db.String(64))
    VM_size = db.Column(db.Float())
    
    def __str__(self):
        return self.VM_uuids  
