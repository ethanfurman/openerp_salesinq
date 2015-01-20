import product
import res_partner
import salesinq

def get_user_reps(obj, cr, uid, context=None):
    user = obj.pool.get('res.user').browse(cr, uid, uid)
    allow_external_si = user.has_group(cr, uid, 'salesinq.user')
    si_rep_text = ''
    if allow_external_si:
        si_webpage = obj.pool.get('salesinq.webpage')
        webpage_rec = si_webpage.browse(cr, uid, [('user_id','=',uid)])
        if not webpage_reg:
            allow_external_si = False
        else:
            reps = []
            for rep in webpage_rec.rep_ids:
                reps.append(rep.code)
            si_rep_text = str(reps)
            crc = '%08X' % (crc32(str(si_rep_text)) & 0xffffffff,)
            xlate = dict(zip("0123456789ABCDEF","ABCDEFGHIJKLMNOP"))
            crc = ''.join([xlate[c] for c in crc[-3:]])
            reps.append(crc)
            si_rep_text = '[' + ','.join(reps) + ']'
    return allow_external_si, si_rep_text
