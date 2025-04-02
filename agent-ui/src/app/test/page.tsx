'use client'

import { useCubeQuery } from '@cubejs-client/react'
import cube from '@cubejs-client/core'

const cubeApi = cube('CUBE-API-TOKEN', {
  apiUrl: 'http://192.168.50.97:30040/cubejs-api/v1'
})

export default function App() {
  useCubeQuery(
    {
      measures: ['chocolate_sales.amount'],
      dimensions: ['chocolate_sales.country']
    },
    {
      cubeApi
    }
  )
  return <>test</>
}
