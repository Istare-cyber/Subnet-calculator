# subnet_gui_split.py
import tkinter as tk
from tkinter import messagebox
from ipaddress import IPv4Interface, IPv4Network, IPv4Address

# -------------------------------------------------------
def dotted_mask_to_prefix(mask: str) -> int:
    try:
        return IPv4Network(f"0.0.0.0/{mask}").prefixlen
    except Exception:
        raise ValueError(f"Masque invalide: {mask}")

# -------------------------------------------------------
def subnet_info(ip: str, prefix_or_mask: str) -> dict:
    if not ip:
        raise ValueError("Veuillez entrer une adresse IP.")
    if not prefix_or_mask:
        raise ValueError("Veuillez entrer un masque ou un /prefix.")

    p = prefix_or_mask.strip()
    if p.startswith("/"):
        p = p[1:]

    prefix = int(p) if p.isdigit() else dotted_mask_to_prefix(p)
    net = IPv4Network((ip.strip(), prefix), strict=False)

    host_bits = 32 - net.prefixlen
    total = 2 ** host_bits

    if net.prefixlen <= 30:
        usable = total - 2
        first_host = IPv4Address(int(net.network_address) + 1)
        last_host  = IPv4Address(int(net.broadcast_address) - 1)
    elif net.prefixlen == 31:
        usable = 0
        first_host = last_host = None
    else:
        usable = 1
        first_host = last_host = net.network_address

    magic = None
    for o in str(net.netmask).split("."):
        v = int(o)
        if v < 255:
            magic = 256 - v
            break

    return {
        "input": f"{ip}/{net.prefixlen}",
        "mask": str(net.netmask),
        "prefixlen": net.prefixlen,
        "host_bits": host_bits,
        "network": str(net.network_address),
        "broadcast": str(net.broadcast_address),
        "total": total,
        "usable": usable,
        "first": None if first_host is None else str(first_host),
        "last":  None if last_host  is None else str(last_host),
        "magic": magic,
    }

# -------------------------------------------------------
def on_calculate():
    ip = ip_var.get().strip()
    m  = mask_var.get().strip()
    try:
        info = subnet_info(ip, m)
        out = []
        out.append(f"Entrée           : {info['input']}")
        out.append(f"Masque           : {info['mask']} (/ {info['prefixlen']})")
        out.append(f"Bits hôte        : {info['host_bits']}")
        out.append(f"Adresse réseau   : {info['network']}")
        out.append(f"Broadcast        : {info['broadcast']}")
        out.append(f"Adresses totales : {info['total']}")
        out.append(f"Hôtes utilisables: {info['usable']}")
        if info['first'] and info['last']:
            out.append(f"Plage utilisable : {info['first']}  →  {info['last']}")
        if info['magic'] is not None:
            out.append(f"Nombre magique   : {info['magic']}")

        result_box.config(state="normal")
        result_box.delete("1.0", "end")
        result_box.insert("1.0", "\n".join(out))
        result_box.config(state="disabled")
    except Exception as e:
        messagebox.showerror("Erreur", str(e))

# -------------------------------------------------------
root = tk.Tk()
root.title("Subnet Calc (IPv4)")

frm = tk.Frame(root, padx=12, pady=12)
frm.pack(fill="both", expand=True)

ip_var = tk.StringVar(value="192.168.13.67")
mask_var = tk.StringVar(value="")

tk.Label(frm, text="Adresse IP").grid(row=0, column=0, sticky="w")
tk.Entry(frm, textvariable=ip_var, width=28).grid(row=0, column=1, padx=8, pady=4)

tk.Label(frm, text="Masque ou /prefix").grid(row=1, column=0, sticky="w")
tk.Entry(frm, textvariable=mask_var, width=28).insert(0, "/24")
tk.Entry(frm, textvariable=mask_var, width=28).grid(row=1, column=1, padx=8, pady=4)

tk.Button(frm, text="Calculer", command=on_calculate).grid(row=2, column=0, columnspan=2, pady=8, sticky="we")

result_box = tk.Text(frm, height=12, width=52, state="disabled")
result_box.grid(row=3, column=0, columnspan=2, pady=6)

root.mainloop()
