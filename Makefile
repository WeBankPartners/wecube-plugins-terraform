current_dir=$(shell pwd)
project_name=$(shell basename "${current_dir}")
version=${PLUGIN_VERSION}

clean:
	rm -rf package


image: clean
	docker build -t $(project_name):$(version) .

package: image
	rm -rf package
	mkdir -p package
	cd package && sed -i 's/{{PLUGIN_VERSION}}/$(version)/'  ../register.xml
	cd package && sed -i 's/{{IMAGENAME}}/$(project_name):$(version)/g' ../register.xml
	cd package && sed -i 's/{{CONTAINERNAME}}/$(project_name)-$(version)/g' ../register.xml
	cd package && docker save -o image.tar $(project_name):$(version)
	cp register.xml  package/
	cd package && zip -9 $(project_name)-$(version).zip image.tar register.xml
	cd package && rm -f image.tar
	docker rmi $(project_name):$(version)

upload: package
	$(eval container_id:=$(shell docker run -v $(current_dir)/package:/package -itd --entrypoint=/bin/sh minio/mc))
	docker exec $(container_id) mc config host add wecubeS3 $(s3_server_url) $(s3_access_key) $(s3_secret_key) wecubeS3
	docker exec $(container_id) mc cp /package/$(project_name)-$(version).zip wecubeS3/wecube-plugin-package-bucket
	docker stop $(container_id)
	docker rm -f $(container_id)
	rm -rf $(project_name)-$(version).zip
