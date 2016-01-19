from openerp.osv import osv, fields, expression

import re

import openerp.addons.decimal_precision as dp
import logging



class product_product_send2neworder(osv.TransientModel):
    _name = 'product.product.send2neworder'

    def _get_default_pricelist(self, cr, uid, context=None):
        pricelist = context.get('pricelist', False)
        if not pricelist:
            pricelist=31
        return pricelist
    _columns = {
        "partner_id" : fields.many2one('res.partner', string='Partner'),
        "pricelist_id" : fields.many2one('product.pricelist', string='Pricelist'),
        "user_id" : fields.many2one('res.users', string='Salesperson'),
          
    }
    _default = {
        "pricelist_id" : _get_default_pricelist,
        'user_id': lambda obj, cr, uid, context: uid,

    }



    def send2neworder(self, cr, uid,ids,context=None):

        data=self.read(cr, uid, ids[0], ['partner_id','pricelist_id'])
        order_obj= self.pool.get('sale.order')
        product_obj= self.pool.get('product.product')
        
        order={}
        order['pricelist_id']=data['pricelist_id'][0]
        order['partner_id']=data['partner_id'][0]
        order['order_line']=[]
        order['user_id']=uid


        for id in context['active_ids']:
            product=product_obj.browse(cr,uid,id)
            line={'product_id':id}
            order['order_line'].append((0,0,line))
        order_id=order_obj.create(cr,uid,order,context=context)



        ir_model_data = self.pool.get('ir.model.data')
        form_res = ir_model_data.get_object_reference(cr, uid, 'sale', 'view_order_form')
        form_id = form_res and form_res[1] or False


        return {
            'name': 'Nueva orden',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': order_id,
            'view_id': False,
            'target' : 'current',
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
        }


    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        if not part:
            return {'value': { 'pricelist_id': False}}
        part = self.pool.get('res.partner').browse(cr, uid, part, context=context)

        pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
        val = {}

        if pricelist:
            val['pricelist_id'] = pricelist
        return {'value': val}
