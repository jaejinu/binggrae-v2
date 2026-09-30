import * as THREE from 'three'

/** Fine material variation without changing the authored label geometry. */
export function finishProduct(root: THREE.Object3D) {
  let grain: THREE.DataTexture | undefined
  root.traverse(o => {
    const mesh=o as THREE.Mesh
    if(!mesh.isMesh)return
    const materials=(Array.isArray(mesh.material)?mesh.material:[mesh.material]).map(m=>{
      if(!(m instanceof THREE.MeshStandardMaterial))return m
      const mat=m.clone()
      if(/wafer|waffle|baked/i.test(mat.name)){
        if(!grain){const data=new Uint8Array(64*64*4);let seed=17;for(let i=0;i<data.length;i+=4){seed=(seed*1664525+1013904223)>>>0;const n=145+(seed%90);data.set([n,n,n,255],i)}grain=new THREE.DataTexture(data,64,64);grain.wrapS=grain.wrapT=THREE.RepeatWrapping;grain.repeat.set(7,7);grain.needsUpdate=true}
        mat.bumpMap=grain;mat.bumpScale=.012;mat.roughness=.82
      }else if(/foil/i.test(mat.name)){mat.metalness=.32;mat.roughness=.25}
      else if(/plastic|shoulder/i.test(mat.name)){mat.roughness=.32}
      else if(/ice cream|vanilla/i.test(mat.name)){mat.roughness=.68}
      mat.needsUpdate=true;return mat
    })
    mesh.material=Array.isArray(mesh.material)?materials:materials[0]!
  })
}

export function prepareSleeve(root: THREE.Object3D) {
  if(root.getObjectByName('Sleeve_Assembly'))return
  const sleeve=root.getObjectByName('Red_Paper_Sleeve');if(!sleeve?.parent)return
  const assembly=new THREE.Group();assembly.name='Sleeve_Assembly';sleeve.parent.add(assembly)
  for(const name of ['Red_Paper_Sleeve','Sleeve_Name','Sleeve_Brand','Sleeve_Since','Back_Tagline','Back_Edition']){const obj=root.getObjectByName(name);if(obj)assembly.attach(obj)}
}
